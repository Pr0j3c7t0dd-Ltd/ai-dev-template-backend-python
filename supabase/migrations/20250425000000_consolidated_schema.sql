-- Consolidated schema migration
-- This migration contains the complete database schema as of April 23, 2025
-- It replaces all previous migrations for a clean setup

-- First drop all existing tables and functions to ensure a clean state
DROP FUNCTION IF EXISTS public.check_user_exists(uuid) CASCADE;
DROP FUNCTION IF EXISTS public.ensure_user_settings() CASCADE;
DROP FUNCTION IF EXISTS public.handle_created_at() CASCADE;
DROP FUNCTION IF EXISTS public.handle_updated_at() CASCADE;
DROP FUNCTION IF EXISTS public.handle_new_user() CASCADE;
DROP TABLE IF EXISTS public.user_settings CASCADE;

-- Reset database to a clean state

-- Create timestamp handling functions
CREATE OR REPLACE FUNCTION public.handle_created_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.created_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create user creation handler function
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
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
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Add comments to explain functions
COMMENT ON FUNCTION public.handle_created_at IS
'Automatically sets the created_at timestamp to current time for new records.';
COMMENT ON FUNCTION public.handle_updated_at IS
'Automatically updates the updated_at timestamp to current time when records are modified.';
COMMENT ON FUNCTION public.handle_new_user IS
'Automatically creates user settings when a new user signs up via Supabase Auth. Uses SECURITY DEFINER to bypass RLS safely.';

-- Now recreate everything in the correct order
CREATE TABLE IF NOT EXISTS public.user_settings (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    theme TEXT DEFAULT 'light',
    language TEXT DEFAULT 'en',
    timezone TEXT DEFAULT 'UTC',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;

-- Create the check_user_exists function
CREATE OR REPLACE FUNCTION public.check_user_exists(user_id_param UUID)
RETURNS JSONB SECURITY DEFINER AS $$
DECLARE
    user_exists BOOLEAN;
BEGIN
    -- Check if the user exists in auth.users
    SELECT EXISTS(
        SELECT 1 FROM auth.users WHERE id = user_id_param
    ) INTO user_exists;
    -- Return the result as a JSONB object
    RETURN jsonb_build_object('exists', user_exists);
END;
$$ LANGUAGE plpgsql;

-- Set proper permissions
REVOKE ALL ON FUNCTION public.check_user_exists(UUID) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.check_user_exists(UUID) TO authenticated;

-- Add function documentation
COMMENT ON FUNCTION public.check_user_exists IS
'Checks if a user with the given UUID exists in the auth.users table.\nReturns a JSONB object with an "exists" boolean field.\nThis function is used by the application to validate user existence before creating settings.\nOnly authenticated users can execute this function.';

-- Create the ensure_user_settings function
CREATE OR REPLACE FUNCTION public.ensure_user_settings()
RETURNS JSONB SECURITY DEFINER AS $$
DECLARE
    user_id UUID;
    settings_record JSONB;
    user_exists BOOLEAN;
BEGIN
    -- Get the current user id
    user_id := auth.uid();
    -- Ensure this function can only be run by authenticated users
    IF user_id IS NULL THEN
        RAISE EXCEPTION 'Not authenticated';
    END IF;
    -- Check if the user exists in auth.users
    SELECT EXISTS(
        SELECT 1 FROM auth.users WHERE id = user_id
    ) INTO user_exists;
    -- If user doesn't exist, raise a clear error
    IF NOT user_exists THEN
        RAISE EXCEPTION 'User ID % does not exist in auth.users table', user_id;
    END IF;
    -- Create user_settings entry if it doesn't exist
    INSERT INTO public.user_settings (
        id,
        theme,
        language,
        timezone
    )
    VALUES (
        user_id,
        'light',
        'en',
        'UTC'
    )
    ON CONFLICT (id) DO NOTHING;
    -- Return the settings for convenience
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
$$ LANGUAGE plpgsql;

-- Set permissions for ensure_user_settings
REVOKE ALL ON FUNCTION public.ensure_user_settings() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.ensure_user_settings() TO authenticated;

-- Set permissions for handle_new_user function
REVOKE ALL ON FUNCTION public.handle_new_user() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO supabase_auth_admin;

-- Add function documentation
COMMENT ON FUNCTION public.ensure_user_settings IS
'Creates user settings for the current user if they don''t exist and returns the settings.\nChecks if the user exists in auth.users before attempting to create settings.\nCall this after authentication if needed.';

-- Grant necessary table permissions
GRANT SELECT, INSERT, UPDATE ON TABLE public.user_settings TO authenticated;
GRANT ALL ON TABLE public.user_settings TO supabase_auth_admin;

-- Create RLS policies
-- 1. SELECT policy - Allow users to view their own settings
CREATE POLICY "Users can view only their own settings"
    ON public.user_settings
    FOR SELECT
    TO authenticated
    USING (auth.uid() = id);

-- 2. INSERT policy - Allow users to insert their own settings
CREATE POLICY "Users can insert their own settings"
    ON public.user_settings
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = id);

-- 3. UPDATE policy - Allow users to update their own settings
CREATE POLICY "Users can update only their own settings"
    ON public.user_settings
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = id);

-- 4. Admin policies - full access for service_role
CREATE POLICY "Service role can manage any user settings"
    ON public.user_settings
    FOR ALL
    TO service_role
    USING (true);

-- 5. Auth admin policy - access for auth admin
CREATE POLICY "Auth admin can manage user settings"
    ON public.user_settings
    FOR ALL
    TO supabase_auth_admin
    USING (true);

-- 6. Postgres role policy - needed for triggers
CREATE POLICY "Postgres role can manage user settings"
    ON public.user_settings
    FOR ALL
    TO postgres
    USING (true);

-- Set up timestamp triggers
CREATE TRIGGER set_user_settings_created_at
BEFORE INSERT ON public.user_settings
FOR EACH ROW
EXECUTE FUNCTION public.handle_created_at();

CREATE TRIGGER set_user_settings_updated_at
BEFORE UPDATE ON public.user_settings
FOR EACH ROW
EXECUTE FUNCTION public.handle_updated_at();

-- Set up user creation trigger
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION public.handle_new_user();

-- Add comprehensive comment for clarity
COMMENT ON TABLE public.user_settings IS
'User settings table that extends auth.users with application-specific settings.\nThis table has RLS enabled with policies to ensure:\n1. Users can only view their own settings\n2. Users can only update their own settings\n3. The handle_new_user trigger function can create settings for new users\n4. Service roles and admin roles can manage any record';
