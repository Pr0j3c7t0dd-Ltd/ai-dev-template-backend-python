-- Create a function to ensure user_settings exists for authenticated users
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if user_settings entry exists, if not create one
    INSERT INTO public.user_settings (id)
    VALUES (NEW.id)
    ON CONFLICT (id) DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Set up trigger on auth.users table for new signups
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION public.handle_new_user();

-- Create a function that can be called from RPC to ensure user settings exist
CREATE OR REPLACE FUNCTION public.ensure_user_settings()
RETURNS void SECURITY DEFINER AS $$
BEGIN
    -- Create user_settings entry if it doesn't exist
    INSERT INTO public.user_settings (id)
    VALUES (auth.uid())
    ON CONFLICT (id) DO NOTHING;
END;
$$ LANGUAGE plpgsql;

-- Add comment to explain how this works
COMMENT ON FUNCTION public.ensure_user_settings IS
'Creates a user_settings record for the authenticated user if one does not exist. Call this after authentication.';
