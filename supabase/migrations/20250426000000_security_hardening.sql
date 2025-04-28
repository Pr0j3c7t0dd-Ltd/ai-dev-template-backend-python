-- Security-hardening migration – ensures best-practice RLS and function safety
-- Created 26 Apr 2025

-- 1. Lock down SECURITY DEFINER functions with an explicit search_path to avoid search-path spoofing.
-- 2. Prevent user-id enumeration in public.check_user_exists.
-- 3. Make UPDATE RLS policy explicit with WITH CHECK.
-- 4. Re-document risks around service_role and ensure no accidental DELETE privilege.

-- ============================================
-- 1. Re-create SECURITY DEFINER functions with SET search_path
-- ============================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    -- Insert the user settings record with explicit defaults
    INSERT INTO public.user_settings (
        id,
        theme,
        language,
        timezone
    )
    VALUES (
        NEW.id,
        'light',
        'en',
        'UTC'
    )
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION public.ensure_user_settings()
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    user_id        UUID;
    settings_record JSONB;
    user_exists    BOOLEAN;
BEGIN
    -- Enforce authentication
    user_id := auth.uid();
    IF user_id IS NULL THEN
        RAISE EXCEPTION 'Not authenticated';
    END IF;
    -- Verify user exists
    SELECT EXISTS(SELECT 1 FROM auth.users WHERE id = user_id) INTO user_exists;
    IF NOT user_exists THEN
        RAISE EXCEPTION 'User ID % does not exist in auth.users table', user_id;
    END IF;
    -- Create settings row if missing
    INSERT INTO public.user_settings (id, theme, language, timezone)
    VALUES (user_id, 'light', 'en', 'UTC')
    ON CONFLICT (id) DO NOTHING;
    -- Return the up-to-date settings
    SELECT jsonb_build_object(
        'id', id,
        'theme', theme,
        'language', language,
        'timezone', timezone
    ) INTO settings_record
    FROM public.user_settings
    WHERE id = user_id;
    RETURN settings_record;
END;
$$;

-- Restrict enumeration and lock search_path
CREATE OR REPLACE FUNCTION public.check_user_exists(user_id_param UUID)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    user_exists BOOLEAN;
BEGIN
    -- Must be authenticated
    IF auth.uid() IS NULL THEN
        RAISE EXCEPTION 'Not authenticated';
    END IF;
    -- Users can only enquire about themselves; admins can check anyone
    IF user_id_param <> auth.uid()
       AND current_user NOT IN ('service_role', 'supabase_auth_admin') THEN
        RAISE EXCEPTION 'Permission denied';
    END IF;
    SELECT EXISTS(SELECT 1 FROM auth.users WHERE id = user_id_param)
    INTO user_exists;
    RETURN jsonb_build_object('exists', user_exists);
END;
$$;

-- Re-grant function privileges (explicit revokes first for idempotency)
REVOKE ALL ON FUNCTION public.check_user_exists(UUID) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.check_user_exists(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.check_user_exists(UUID) TO supabase_auth_admin;
REVOKE ALL ON FUNCTION public.ensure_user_settings() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.ensure_user_settings() TO authenticated;
REVOKE ALL ON FUNCTION public.handle_new_user() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO supabase_auth_admin;

-- ============================================
-- 2. Harden RLS policies
-- ============================================
-- Replace UPDATE policy with explicit WITH CHECK clause
DROP POLICY IF EXISTS "Users can update only their own settings" ON public.user_settings;
CREATE POLICY "Users can update only their own settings"
    ON public.user_settings
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Optional: explicitly deny DELETE to authenticated role (defence-in-depth)
REVOKE DELETE ON public.user_settings FROM authenticated;

-- ============================================
-- 3. Audit comment to highlight service_role use
-- ============================================
COMMENT ON POLICY "Service role can manage any user settings" ON public.user_settings IS
'Full access for service_role. NEVER expose the service-role key client-side. See https://www.supadex.app/blog/best-security-practices-in-supabase-a-comprehensive-guide for guidance.';

-- Migration complete.
