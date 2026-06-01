package com.keeeensy.rpglevels;

import net.fabricmc.api.ClientModInitializer;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3fc;

public class RPGLevelsClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
    }

    public static boolean isLevelMob(LivingEntity entity) {
        return entity instanceof Monster
            && entity.hasCustomName()
            && entity.getCustomName().getString().startsWith(RPGLevelsMod.LEVEL_PREFIX);
    }

    public static Entity getCrosshairTarget() {
        Minecraft mc = Minecraft.getInstance();
        if (mc == null || mc.player == null) {
            return null;
        }

        HitResult hit = mc.hitResult;
        if (hit != null && hit.getType() == HitResult.Type.ENTITY) {
            return ((EntityHitResult) hit).getEntity();
        }

        Entity picked = mc.getEntityRenderDispatcher().crosshairPickEntity;
        if (picked != null) {
            return picked;
        }

        return null;
    }

    public static boolean isCrosshairTarget(LivingEntity entity) {
        Entity target = getCrosshairTarget();
        if (target != null && target.getId() == entity.getId()) return true;
        return isEntityUnderCrosshair(entity);
    }

    public static boolean hasLineOfSight(LivingEntity entity) {
        Minecraft mc = Minecraft.getInstance();
        if (mc == null || mc.level == null) return false;

        Vec3 from = mc.gameRenderer.getMainCamera().position();
        Vec3 to = entity.getEyePosition();

        if (from.distanceToSqr(to) < 1.0) return true;

        ClipContext ctx = new ClipContext(from, to, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, entity);
        return mc.level.clip(ctx).getType() == HitResult.Type.MISS;
    }

    private static boolean isEntityUnderCrosshair(LivingEntity entity) {
        Minecraft mc = Minecraft.getInstance();
        if (mc == null || mc.level == null) return false;

        Vector3fc fwd = mc.gameRenderer.getMainCamera().forwardVector();
        Vec3 from = mc.gameRenderer.getMainCamera().position();
        Vec3 dir = new Vec3(fwd.x(), fwd.y(), fwd.z());
        Vec3 to = from.add(dir.scale(256.0));

        AABB bb = entity.getBoundingBox().inflate(0.1);
        java.util.Optional<Vec3> hit = bb.clip(from, to);
        if (hit.isEmpty()) return false;

        ClipContext ctx = new ClipContext(from, hit.get(), ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, entity);
        return mc.level.clip(ctx).getType() == HitResult.Type.MISS;
    }
}
