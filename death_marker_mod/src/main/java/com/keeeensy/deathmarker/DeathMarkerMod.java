package com.keeeensy.deathmarker;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DeathMarkerMod implements ModInitializer {
    public static final Logger LOGGER = LoggerFactory.getLogger("death-marker");

    @Override
    public void onInitialize() {
        ServerLivingEntityEvents.AFTER_DEATH.register((entity, source) -> {
            if (!(entity instanceof Player player)) return;

            ServerLevel level = (ServerLevel) player.level();
            BlockPos deathPos = player.blockPosition();
            BlockPos placePos = findPlacePos(level, deathPos);

            if (placePos != null) {
                level.setBlock(placePos, Blocks.SOUL_TORCH.defaultBlockState(), 3);
                level.sendParticles(ParticleTypes.SOUL,
                    placePos.getX() + 0.5, placePos.getY() + 0.5, placePos.getZ() + 0.5,
                    30, 0.5, 0.5, 0.5, 0.05);
                LOGGER.info("Death marker placed at {} for {}", placePos, player.getName().getString());
            } else {
                level.sendParticles(ParticleTypes.SOUL,
                    player.getX(), player.getY() + 1, player.getZ(),
                    30, 0.5, 0.5, 0.5, 0.05);
                LOGGER.info("Death marker (no placement) for {} at ({}, {}, {})",
                    player.getName().getString(),
                    String.format("%.1f", player.getX()),
                    String.format("%.1f", player.getY()),
                    String.format("%.1f", player.getZ()));
            }
        });

        LOGGER.info("Death Marker Mod initialized!");
    }

    private BlockPos findPlacePos(ServerLevel level, BlockPos pos) {
        for (int dy = 0; dy >= -1; --dy) {
            for (int dx = -1; dx <= 1; ++dx) {
                for (int dz = -1; dz <= 1; ++dz) {
                    BlockPos check = pos.offset(dx, dy, dz);
                    if (canPlaceTorch(level, check)) return check;
                }
            }
        }
        return null;
    }

    private boolean canPlaceTorch(ServerLevel level, BlockPos pos) {
        BlockState state = level.getBlockState(pos);
        if (!state.isAir()) return false;
        BlockPos below = pos.below();
        BlockState belowState = level.getBlockState(below);
        return belowState.isSolid();
    }
}
