package com.keeeensy.rpglevels;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.TextColor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public class RPGLevelsMod implements ModInitializer {
    public static final Logger LOGGER = LoggerFactory.getLogger("rpg-levels");
    public static final String LEVEL_PREFIX = "Lvl ";
    private static final Map<UUID, Integer> mobLevels = new ConcurrentHashMap<>();

    @Override
    public void onInitialize() {
        ServerLivingEntityEvents.AFTER_DEATH.register((entity, source) -> {
            if (entity instanceof Monster le && source.getEntity() instanceof ServerPlayer player) {
                int level = getMobLevel(le);
                int xp = level * 10;
                player.giveExperiencePoints(xp);
                player.sendSystemMessage(Component.literal("+" + xp + " XP (mob level " + level + ")"));
            }
        });
        LOGGER.info("RPG Levels Mod initialized!");
    }

    public static int getMobLevel(LivingEntity entity) {
        return mobLevels.computeIfAbsent(entity.getUUID(), id -> {
            int base = 1;
            if (entity.level() != null) {
                Player nearest = entity.level().getNearestPlayer(entity, 32);
                if (nearest instanceof ServerPlayer sp) {
                    base = Math.max(1, sp.experienceLevel);
                }
            }
            return Math.max(1, base + (int)(Math.random() * 5) - 1);
        });
    }

    public static String getLevelColor(int level) {
        float t = Math.min(1.0f, (level - 1) / 99.0f);
        int r = Math.max(0, 255 - (int)(t * 205));
        int g = Math.max(0, 255 - (int)(t * 255));
        int b = Math.max(0, 255 - (int)(t * 175));
        return String.format("#%02x%02x%02x", r, g, b);
    }

    public static void setLevelDisplay(LivingEntity entity) {
        int level = getMobLevel(entity);
        TextColor color = TextColor.parseColor(getLevelColor(level)).getOrThrow();
        String typeName = entity.getType().getDescription().getString();
        Component name = Component.literal(LEVEL_PREFIX + level + " " + typeName).withStyle(s -> s.withColor(color));
        entity.setCustomName(name);
        entity.setCustomNameVisible(false);
    }

    public static float calcDamageModifier(int mobLevel, int playerLevel) {
        if (playerLevel < 1) playerLevel = 1;
        if (mobLevel < 1) mobLevel = 1;
        float ratio = (float) mobLevel / playerLevel;
        if (ratio > 1.0f) {
            return 1.0f / ratio;
        }
        return 0.5f + 0.5f / Math.max(0.01f, ratio);
    }
}
