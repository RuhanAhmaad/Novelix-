import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('image') as File | null;

    if (!file) {
      return NextResponse.json({ error: 'No image file provided' }, { status: 400 });
    }

    // Validate mime type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
      return NextResponse.json(
        { error: 'Invalid file format. Please upload JPG, PNG, or WebP.' },
        { status: 400 }
      );
    }

    // Validate size (max 16MB)
    const MAX_SIZE = 16 * 1024 * 1024;
    if (file.size > MAX_SIZE) {
      return NextResponse.json(
        { error: 'Image size exceeds maximum limit of 16MB.' },
        { status: 400 }
      );
    }

    const apiKey = process.env.IMGBB_API_KEY;
    if (!apiKey) {
      return NextResponse.json({ error: 'Image service unconfigured. Use Firebase Storage.' }, { status: 500 });
    }

    // Convert file to base64
    const buffer = await file.arrayBuffer();
    const base64Image = Buffer.from(buffer).toString('base64');

    // Send to ImgBB API
    const imgbbForm = new URLSearchParams();
    imgbbForm.append('key', apiKey);
    imgbbForm.append('image', base64Image);
    imgbbForm.append('name', file.name.replace(/\.[^/.]+$/, ''));

    const res = await fetch('https://api.imgbb.com/1/upload', {
      method: 'POST',
      body: imgbbForm,
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      return NextResponse.json(
        { error: data?.error?.message || 'Failed to upload image to ImgBB' },
        { status: res.status || 500 }
      );
    }

    return NextResponse.json({
      success: true,
      url: data.data.url,
      display_url: data.data.display_url,
      thumb_url: data.data.thumb?.url || data.data.display_url,
      width: data.data.width,
      height: data.data.height,
      delete_url: data.data.delete_url,
    });
  } catch (error: any) {
    console.error('ImgBB Upload Error:', error);
    return NextResponse.json(
      { error: error.message || 'An error occurred during upload' },
      { status: 500 }
    );
  }
}
