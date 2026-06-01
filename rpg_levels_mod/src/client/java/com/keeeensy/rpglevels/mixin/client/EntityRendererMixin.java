package com.keeeensy.rpglevels.mixin.client;

import com.keeeensy.rpglevels.RPGLevelsClient;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(LivingEntityRenderer.class)
public abstract class EntityRendererMixin<T extends LivingEntity, S> {

    @Inject(method = "shouldShowName", at = @At("RETURN"), cancellable = true)
    private void rpgLevels$showLevelOnlyOnCrosshair(T entity, double distance, CallbackInfoReturnable<Boolean> cir) {
        if (!RPGLevelsClient.isLevelMob(entity)) {
            return;
        }
        cir.setReturnValue(RPGLevelsClient.isCrosshairTarget(entity));
    }
}
