-- Migration: 001_create_memory_tables.sql
-- Description: Create speech_corrections and phrase_frequencies tables for PEEXH personal speech memory (RFC-005)

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 1. Speech Correction Pairs Table
-- Maps previously misrecognized or distorted speech transcripts to the user's verified intended phrase
CREATE TABLE IF NOT EXISTS speech_corrections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL DEFAULT 'default_user',
    raw_transcript TEXT NOT NULL,
    corrected_phrase TEXT NOT NULL,
    frequency INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for exact user + transcript lookup
CREATE INDEX IF NOT EXISTS idx_corrections_user_raw 
ON speech_corrections (user_id, raw_transcript);

-- Trigram index for fuzzy/similarity text search
CREATE INDEX IF NOT EXISTS idx_corrections_trgm 
ON speech_corrections USING gin (raw_transcript gin_trgm_ops);


-- 2. Phrase Frequencies Table
-- Tracks how often the user communicates specific phrases to reinforce active vocabulary
CREATE TABLE IF NOT EXISTS phrase_frequencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL DEFAULT 'default_user',
    phrase TEXT NOT NULL,
    use_count INT NOT NULL DEFAULT 1,
    last_used_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_phrase UNIQUE (user_id, phrase)
);

-- Index for ordering by frequent usage
CREATE INDEX IF NOT EXISTS idx_phrase_freq_user_count 
ON phrase_frequencies (user_id, use_count DESC);
