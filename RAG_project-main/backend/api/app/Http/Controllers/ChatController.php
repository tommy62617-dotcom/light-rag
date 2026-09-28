<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ChatController extends Controller
{
    public function ask(Request $request): JsonResponse
    {
        $validated = $request->validate([
            "query" => "required|string|max:1000",
            "scenario" => "nullable|string|in:compliance_planning,sop_check,incident_analysis,prework_check",
            "model" => "nullable|string",
        ]);

        $apiUrl = config("services.fastapi.url", "http://127.0.0.1:8001");
        $timeout = config("services.fastapi.timeout", 180);

        try {
            $response = Http::timeout($timeout)
                ->acceptJson()
                ->post("{$apiUrl}/api/v1/chat", [
                    "query" => $validated["query"],
                    "scenario" => $validated["scenario"] ?? "compliance_planning",
                    "model" => $validated["model"] ?? "llama3",
                ]);

            if ($response->failed()) {
                Log::error("FastAPI 服務回應異常", ["status" => $response->status(), "body" => $response->body()]);
                return response()->json([
                    "status" => "error",
                    "message" => "AI 服務暫時無法回應，請稍後再試。"
                ], $response->status() >= 500 ? 502 : $response->status());
            }

            return response()->json([
                "status" => "success",
                "data" => $response->json(),
            ]);

        } catch (\Illuminate\Http\Client\ConnectionException $e) {
            Log::critical("無法連線至 FastAPI 微服務", ["error" => $e->getMessage()]);
            return response()->json([
                "status" => "error",
                "message" => "無法連線至 AI 計算節點。"
            ], 504);
        }
    }
}
