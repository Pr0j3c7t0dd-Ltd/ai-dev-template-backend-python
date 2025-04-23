-- Consolidated migration for properly setting up user_settings table with RLS
-- This combines all the fixes from previous migrations

-- Re-enable RLS if it wasn't already enabled
ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;

-- Drop any existing policies to start fresh
DROP POLICY IF EXISTS "Users can view only their own settings" ON public.user_settings;
DROP POLICY IF EXISTS "Users can insert their own settings" ON public.user_settings;
DROP POLICY IF EXISTS "Users can update their own settings" ON public.user_settings;
DROP POLICY IF EXISTS "Users and auth service can insert settings" ON public.user_settings;
DROP POLICY IF EXISTS "Auth admin can insert any user settings" ON public.user_settings;
DROP POLICY IF EXISTS "Auth admin can update any user settings" ON public.user_settings;
DROP POLICY IF EXISTS "Insert user settings" ON public.user_settings;
DROP POLICY IF EXISTS "Service role can manage any record" ON public.user_settings;
DROP POLICY IF EXISTS "Allow postgres role to insert user settings" ON public.user_settings;

-- Grant necessary permissions
GRANT ALL ON TABLE public.user_settings TO supabase_auth_admin;
GRANT SELECT, INSERT, UPDATE ON TABLE public.user_settings TO authenticated;

-- Create proper RLS policies
-- 1. View policy - users can only view their own settings
CREATE POLICY "Users can view only their own settings"
    ON public.user_settings
    FOR SELECT
    USING (auth.uid() = id);

-- 2. Update policy - users can only update their own settings
CREATE POLICY "Users can update only their own settings"
    ON public.user_settings
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = id);

-- 3. Insert policy - authenticated users can insert their own settings
CREATE POLICY "Users can insert their own settings"
    ON public.user_settings
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = id);

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

-- Create a properly secured handle_new_user function
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert the user settings record
    -- SECURITY DEFINER allows this function to bypass RLS
    INSERT INTO public.user_settings (id)
    VALUES (NEW.id)
    ON CONFLICT (id) DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Make sure function permissions are correct
REVOKE ALL ON FUNCTION public.handle_new_user() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO supabase_auth_admin;

-- Comment on the function to explain its purpose
COMMENT ON FUNCTION public.handle_new_user IS
'Automatically creates a user_settings record when a new user signs up. Uses SECURITY DEFINER to bypass RLS.';

-- Drop and recreate the trigger to ensure it works
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION public.handle_new_user();

-- Add comprehensive comment for clarity
COMMENT ON TABLE public.user_settings IS
'User settings table that extends auth.users with application-specific settings.
This table has RLS enabled with policies to ensure:
1. Users can only view their own settings
2. Users can only update their own settings
3. The handle_new_user trigger function can create settings for new users
4. Service roles and admin roles can manage any record';
