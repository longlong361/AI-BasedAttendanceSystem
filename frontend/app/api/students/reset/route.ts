import { NextResponse } from 'next/server';
import { supabaseClient } from '@/lib/supabase';

export async function POST() {
  try {
    const { error } = await supabaseClient
      .from('students')
      .update({ status: 'absent' })
      .neq('status', 'absent'); // Update all that are not already absent

    if (error) {
      return NextResponse.json(
        { success: false, error: error.message },
        { status: 400 }
      );
    }

    return NextResponse.json({ success: true }, { status: 200 });
  } catch (err) {
    return NextResponse.json(
      { success: false, error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}
