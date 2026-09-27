CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS public.students (
  id uuid primary key default gen_random_uuid(),
  student_code text unique not null,
  name text not null,
  class_name text,
  school text,
  status text default 'absent',
  face_vector vector(512),
  created_at timestamp with time zone default timezone('utc'::text, now())
);

CREATE OR REPLACE FUNCTION match_face (
  query_embedding vector(512),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id uuid,
  student_code text,
  name text,
  class_name text,
  school text,
  similarity float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    students.id,
    students.student_code,
    students.name,
    students.class_name,
    students.school,
    1 - (students.face_vector <=> query_embedding) AS similarity
  FROM students
  WHERE 1 - (students.face_vector <=> query_embedding) > match_threshold
  ORDER BY students.face_vector <=> query_embedding
  LIMIT match_count;
$$;