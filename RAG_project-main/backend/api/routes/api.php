<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ChatController;

Route::prefix('v1')->group(function () {
    Route::post('/chat', [ChatController::class, 'ask']);
});