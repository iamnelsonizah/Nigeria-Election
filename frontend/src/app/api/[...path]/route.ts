import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.FASTAPI_URL ?? "http://127.0.0.1:8000";

type RouteContext = {
  params: Promise<{
    path: string[];
  }>;
};

export async function GET(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const target = new URL(`/api/${path.join("/")}`, API_BASE_URL);
  target.search = request.nextUrl.search;

  try {
    const response = await fetch(target, {
      headers: { accept: "application/json" },
      cache: "no-store",
    });

    const body = await response.text();
    return new NextResponse(body, {
      status: response.status,
      headers: {
        "content-type": response.headers.get("content-type") ?? "application/json",
      },
    });
  } catch {
    return NextResponse.json(
      {
        detail: "FastAPI backend is unavailable. Start it with npm run api from the project root.",
      },
      { status: 502 }
    );
  }
}

export async function POST(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const target = new URL(`/api/${path.join("/")}`, API_BASE_URL);

  try {
    const reqBody = await request.text();
    const response = await fetch(target, {
      method: "POST",
      headers: {
        "content-type": request.headers.get("content-type") ?? "application/json",
        accept: "application/json",
      },
      body: reqBody,
      cache: "no-store",
    });

    const body = await response.text();
    return new NextResponse(body, {
      status: response.status,
      headers: {
        "content-type": response.headers.get("content-type") ?? "application/json",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        detail: `FastAPI backend error: ${(error as Error).message}`,
      },
      { status: 502 }
    );
  }
}
