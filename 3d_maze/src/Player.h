#pragma once
#include "raylib.h"

class Maze;

class Player {
public:
    Player();

    void Update(float dt, const Maze& maze, int screenW, int screenH);
    void Reset(const Vector3& spawnPos);

    void SetSensitivity(float s) { m_sensitivity = s; }
    Camera3D* GetCamera() { return &m_camera; }
    Vector3 GetPosition() const { return m_position; }

private:
    Camera3D m_camera;
    Vector3 m_position;
    Vector3 m_forward;

    float m_yaw = 0.0f;
    float m_pitch = 0.0f;
    float m_walkSpeed = 6.0f;
    float m_sprintMultiplier = 1.8f;
    float m_sensitivity = 0.003f;
    float m_radius = 0.25f;
    float m_height = 1.6f;
};
