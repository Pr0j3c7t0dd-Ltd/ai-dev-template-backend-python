# Supabase Migrations

This directory contains database migrations for the Supabase project.

## Migrations

- **20240401000000_initial_schema.sql**: Initial database schema, creates the user_settings table and sets up RLS
- **20250331203401_auto_create_user_settings.sql**: Adds triggers to automatically create user settings when a user registers
- **20250423174800_ensure_rls_enabled.sql**: Ensures RLS is properly enabled on the user_settings table

## Applying Migrations

Migrations are automatically applied when running `supabase start` locally, or when deploying to a Supabase project.

To manually apply migrations to a local Supabase instance:

```bash
supabase migration up
```

To apply migrations to a remote Supabase instance:

```bash
supabase db push
```

## Row-Level Security (RLS)

The user_settings table has RLS enabled with policies that ensure:
1. Users can only view their own settings
2. Users can only insert their own settings
3. Users can only update their own settings

If RLS is not working properly, the migration `20250423174800_ensure_rls_enabled.sql` can be applied to fix the issue.
