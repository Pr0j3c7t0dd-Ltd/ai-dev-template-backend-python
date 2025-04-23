-- Migration to ensure RLS is properly enabled on user_settings table
-- This re-applies the RLS settings that should have been applied in the initial migration

-- First check if the table exists
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_settings') THEN
        -- Re-enable Row Level Security (in case it was disabled)
        ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;

        -- Drop existing policies if they exist
        DROP POLICY IF EXISTS "Users can view only their own settings" ON public.user_settings;
        DROP POLICY IF EXISTS "Users can insert their own settings" ON public.user_settings;
        DROP POLICY IF EXISTS "Users can update their own settings" ON public.user_settings;

        -- Re-create strict RLS policies
        CREATE POLICY "Users can view only their own settings"
            ON public.user_settings
            FOR SELECT
            USING (auth.uid() = id);

        CREATE POLICY "Users can insert their own settings"
            ON public.user_settings
            FOR INSERT
            WITH CHECK (auth.uid() = id);

        CREATE POLICY "Users can update their own settings"
            ON public.user_settings
            FOR UPDATE
            USING (auth.uid() = id);

        RAISE NOTICE 'RLS settings re-applied to user_settings table';
    ELSE
        RAISE NOTICE 'user_settings table does not exist';
    END IF;
END
$$;
