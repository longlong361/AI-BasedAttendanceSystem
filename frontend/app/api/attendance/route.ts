'use strict';
import { NextResponse } from 'next/server';
import { supabaseClient } from '@/lib/supabase';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { vector } = body;

    if (!vector || !Array.isArray(vector)) {
      return NextResponse.json(
        { success: false, error: 'Missing or invalid vector in request body' },
        { status: 400 }
      );
    }

    // dùng rpc ném vector cho db tự tính toán luôn cho mượt
    // để threshold 0.4 th k là nhận diện nhầm mấy đứa giống nhau
    const { data, error } = await supabaseClient.rpc('match_face', {
      query_embedding: vector,
      match_threshold: 0.5,
      match_count: 1
    });

    if (error) {
      return NextResponse.json(
        { success: false, error: error.message },
        { status: 400 }
      );
    }

    if (!data || data.length === 0) {
      return NextResponse.json(
        { success: false, error: 'No matching face found' },
        { status: 404 }
      );
    }

    const matchedStudent = data[0];

    // đúng ng thì update status present thôi, k check rườm rà
    const { error: updateError } = await supabaseClient
      .from('students')
      .update({ status: 'present' })
      .eq('id', matchedStudent.id);

    if (updateError) {
      return NextResponse.json(
        { success: false, error: updateError.message },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { success: true, student: matchedStudent },
      { status: 200 }
    );
  } catch (err) {
    return NextResponse.json(
      { success: false, error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}
