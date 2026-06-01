#include "Player.h"
#include "Maze.h"
#include <cmath>
#include "raymath.h"

Player::Player() {
    m_camera.position = {0};
    m_camera.target = {0, 0, -1};
    m_camera.up = {0, 1, 0};
    m_camera.fovy = 80.0f;
    m_camera.projection = CAMERA_PERSPECTIVE;
}

void Player::Reset(const Vector3& spawnPos) {
    m_position = spawnPos;
    m_position.y = m_height;
    m_yaw = 0.0f;
    m_pitch = 0.0f;
    m_forward = {0, 0, -1};
}

void Player::Update(float dt, const Maze& maze, int screenW, int screenH) {
    Vector2 mp = GetMousePosition();
    Vector2 center = { screenW * 0.5f, screenH * 0.5f };
    Vector2 delta = { mp.x - center.x, mp.y - center.y };
    if (fabsf(delta.x) > 0.0f || fabsf(delta.y) > 0.0f) {
        SetMousePosition((int)center.x, (int)center.y);
    }
    m_yaw += -delta.x * m_sensitivity;
    m_pitch += -delta.y * m_sensitivity;
    m_pitch = Clamp(m_pitch, -PI / 2.2f, PI / 2.2f);

    float cp = cosf(m_pitch), sp = sinf(m_pitch);
    float cy = cosf(m_yaw), sy = sinf(m_yaw);
    m_forward = { cp * sy, sp, cp * cy };

    Vector3 right = Vector3Normalize(Vector3CrossProduct(m_forward, {0, 1, 0}));
    Vector3 flatForward = Vector3Normalize({m_forward.x, 0, m_forward.z});

    Vector3 move = {0};
    if (IsKeyDown(KEY_W) || IsKeyDown(KEY_UP)) move = Vector3Add(move, flatForward);
    if (IsKeyDown(KEY_S) || IsKeyDown(KEY_DOWN)) move = Vector3Subtract(move, flatForward);
    if (IsKeyDown(KEY_A) || IsKeyDown(KEY_LEFT)) move = Vector3Subtract(move, right);
    if (IsKeyDown(KEY_D) || IsKeyDown(KEY_RIGHT)) move = Vector3Add(move, right);

    if (fabsf(move.x) > 0.001f || fabsf(move.z) > 0.001f) {
        bool sprint = IsKeyDown(KEY_LEFT_SHIFT) || IsKeyDown(KEY_RIGHT_SHIFT);
        float speed = m_walkSpeed * (sprint ? m_sprintMultiplier : 1.0f);
        move = Vector3Scale(Vector3Normalize(move), speed * dt);

        Vector3 testX = { m_position.x + move.x, m_position.y, m_position.z };
        if (!maze.CheckCollision(testX, m_radius)) {
            m_position.x = testX.x;
        }

        Vector3 testZ = { m_position.x, m_position.y, m_position.z + move.z };
        if (!maze.CheckCollision(testZ, m_radius)) {
            m_position.z = testZ.z;
        }
    }

    m_camera.position = m_position;
    m_camera.target = Vector3Add(m_position, m_forward);
}
