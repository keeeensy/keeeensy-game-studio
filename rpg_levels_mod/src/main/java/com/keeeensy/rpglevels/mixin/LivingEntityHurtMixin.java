package com.keeeensy.rpglevels.mixin;

import com.keeeensy.rpglevels.RPGLevelsMod;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.monster.Monster;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(LivingEntity.class)
public class LivingEntityHurtMixin {
    @Unique
    private boolean rpgLevels$initialized = false;

    @Inject(method = "tick", at = @At("HEAD"))
    private void onTick(CallbackInfo ci) {
        LivingEntity self = (LivingEntity)(Object)this;
        if (!rpgLevels$initialized && self.level() != null && !self.level().isClientSide()) {
            rpgLevels$initialized = true;
            if (self instanceof Monster) {
                RPGLevelsMod.setLevelDisplay(self);
            }
        }
    }

    @ModifyVariable(method = "hurtServer", at = @At("HEAD"), argsOnly = true, ordinal = 0, remap = false)
    private float modifyDamage(float amount, ServerLevel level, DamageSource src, float amt) {
        LivingEntity target = (LivingEntity)(Object)this;
        Entity attacker = src.getEntity();

        if (target instanceof Monster && attacker instanceof ServerPlayer player) {
            int mobLevel = RPGLevelsMod.getMobLevel(target);
            int playerLevel = player.experienceLevel + 1;
            return amount * RPGLevelsMod.calcDamageModifier(mobLevel, playerLevel);
        }

        if (target instanceof ServerPlayer player && attacker instanceof Monster mob) {
            int mobLevel = RPGLevelsMod.getMobLevel(mob);
            int playerLevel = player.experienceLevel + 1;
            float ratio = (float) mobLevel / Math.max(1, playerLevel);
            return ratio > 1.0f ? amount * ratio : amount;
        }

        return amount;
    }
}
