package com.keeeensy.rpglevels.mixin.client;

import com.keeeensy.rpglevels.RPGLevelsClient;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityAttachment;
import net.minecraft.world.entity.monster.Monster;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(EntityRenderer.class)
public abstract class EntityRendererDistanceMixin {

    @Inject(method = "extractRenderState", at = @At("RETURN"))
    private void rpgLevels$extendNameTagDistance(Entity entity, EntityRenderState state, float partialTick, CallbackInfo ci) {
        if (state.nameTag != null) return;
        if (!(entity instanceof Monster mob)) return;
        if (!RPGLevelsClient.isLevelMob(mob)) return;
        if (state.distanceToCameraSq > 65536.0) return;
        if (!RPGLevelsClient.isCrosshairTarget(mob)) return;
        if (!RPGLevelsClient.hasLineOfSight(mob)) return;

        state.nameTag = mob.getDisplayName();
        state.nameTagAttachment = mob.getAttachments().getNullable(EntityAttachment.NAME_TAG, 0, mob.getYRot(partialTick));
    }
}
