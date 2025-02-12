<script lang="ts">
    import { onMount, onDestroy } from "svelte";

    let canvas: HTMLCanvasElement;
    let context: CanvasRenderingContext2D;
    let width: number;
    let height: number;
    let time = 0;
    let velocity = 0.02;
    let velocityTarget = 0.02;
    let colorTime = 0;
    let animationFrameId: number;
    let isDestroyed = false;

    const MAX_OFFSET = 600;
    const SPACING = 4;
    const POINTS = MAX_OFFSET / SPACING;
    const PEAK = MAX_OFFSET * 0.25;
    const POINTS_PER_LAP = 4.444;
    const SHADOW_STRENGTH = 8;
    const COLOR_SPEED = 0.0005;

    onMount(() => {
        setup();
        return () => {
            window.removeEventListener("resize", resize);
        };
    });

    onDestroy(() => {
        isDestroyed = true;
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }
    });

    function setup() {
        context = canvas.getContext("2d")!;
        resize();
        step();
        window.addEventListener("resize", resize);
    }

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }

    function step() {
        if (isDestroyed) return;

        time += velocity;
        colorTime += COLOR_SPEED;
        velocity += (velocityTarget - velocity) * 0.3;
        clear();
        render();
        animationFrameId = requestAnimationFrame(step);
    }

    function clear() {
        context?.clearRect(0, 0, width, height);
    }

    function getGradientColors() {
        const r1 = Math.sin(colorTime) * 127 + 128;
        const g1 = Math.sin(colorTime + 2) * 127 + 128;
        const b1 = Math.sin(colorTime + 4) * 127 + 128;

        const r2 = Math.sin(colorTime + 2) * 127 + 128;
        const g2 = Math.sin(colorTime + 4) * 127 + 128;
        const b2 = Math.sin(colorTime + 6) * 127 + 128;

        const r3 = Math.sin(colorTime + 4) * 127 + 128;
        const g3 = Math.sin(colorTime + 6) * 127 + 128;
        const b3 = Math.sin(colorTime + 8) * 127 + 128;

        return {
            color1: `rgb(${r1},${g1},${b1})`,
            color2: `rgb(${r2},${g2},${b2})`,
            color3: `rgb(${r3},${g3},${b3})`,
        };
    }

    function render() {
        if (!context) return;

        let x, y;
        const cx = width / 2;
        const cy = height / 2;

        context.globalCompositeOperation = "lighter";
        const gradient = context.createLinearGradient(0, 0, width, height);
        const colors = getGradientColors();
        gradient.addColorStop(0, colors.color1);
        gradient.addColorStop(0.5, colors.color2);
        gradient.addColorStop(1, colors.color3);

        context.strokeStyle = gradient;
        context.shadowColor = colors.color2;
        context.lineWidth = 3;
        context.beginPath();

        for (let i = POINTS; i > 0; i--) {
            const value = i * SPACING + (time % SPACING);
            const ax = Math.sin(value / POINTS_PER_LAP) * Math.PI;
            const ay = Math.cos(value / POINTS_PER_LAP) * Math.PI;
            x = ax * value * 1.2;
            y = ay * value * 0.4;
            const o = 1 - Math.min(value, PEAK) / PEAK;
            y -= Math.pow(o, 2) * 200;
            y += (200 * value) / MAX_OFFSET;
            y += (x / cx) * width * 0.1;
            context.globalAlpha = 1 - value / MAX_OFFSET;
            context.shadowBlur = SHADOW_STRENGTH * o;
            context.lineTo(cx + x, cy + y);
            context.stroke();
            context.beginPath();
            context.moveTo(cx + x, cy + y);
        }
        context.lineTo(cx, cy - 200);
        context.lineTo(cx, 0);
        context.stroke();
    }
</script>

<div class="landing-container">
    <canvas bind:this={canvas}></canvas>
    <div class="content">
        <div class="top-right-text">
            <h1 class="main-heading">xiandao</h1>
            <p class="tagline">make your $xian heard</p>
            <div class="cta-buttons">
                <a href="#/proposals" class="cta-button primary"
                    >View Proposals</a
                >
                <a href="#/create-proposal" class="cta-button secondary"
                    >Create Proposal</a
                >
            </div>
        </div>
    </div>
</div>

<style>
    :global(#app) {
        min-height: 100vh;
        width: 100vw;
        background: linear-gradient(45deg, #0f0c29, #302b63, #24243e);
        overflow-x: hidden;
        position: relative;
    }

    :global(body) {
        margin: 0;
        padding: 0;
        min-height: 100vh;
        color: #e0e0e0;
    }

    .landing-container {
        width: 100%;
        height: 100vh;
        position: absolute;
        top: 0;
        left: 0;
        overflow: hidden;
        z-index: 0;
    }

    canvas {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
    }

    .content {
        position: absolute;
        width: 100%;
        height: 100%;
        pointer-events: auto;
    }

    .top-right-text {
        position: absolute;
        top: 15%;
        right: 10%;
        text-align: right;
        max-width: 600px;
    }

    .main-heading {
        font-size: 4.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 0 0 30px rgba(78, 205, 196, 0.3);
    }

    .tagline {
        font-size: 1.8rem;
        color: white;
        opacity: 0.9;
    }

    .cta-buttons {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
        justify-content: flex-end;
    }

    .cta-button {
        padding: 1rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.1rem;
        text-decoration: none;
        transition: all 0.3s ease;
        letter-spacing: 0.5px;
    }

    .cta-button.primary {
        background: linear-gradient(
            135deg,
            rgba(78, 205, 196, 0.8),
            rgba(48, 43, 99, 0.8)
        );
        color: white;
        border: none;
        box-shadow: 0 4px 15px rgba(78, 205, 196, 0.2);
        backdrop-filter: blur(8px);
    }

    .cta-button.secondary {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(78, 205, 196, 0.4);
        backdrop-filter: blur(8px);
    }

    .cta-button:hover {
        transform: translateY(-2px);
    }

    .cta-button.primary:hover {
        background: linear-gradient(
            135deg,
            rgba(78, 205, 196, 0.9),
            rgba(48, 43, 99, 0.9)
        );
        box-shadow: 0 6px 20px rgba(78, 205, 196, 0.3);
    }

    .cta-button.secondary:hover {
        background: rgba(78, 205, 196, 0.15);
        border-color: rgba(78, 205, 196, 0.6);
    }

    @media (max-width: 768px) {
        .top-right-text {
            right: 1rem;
            left: 1rem;
            text-align: center;
        }

        .main-heading {
            font-size: 2.5rem;
        }

        .tagline {
            font-size: 1.2rem;
        }

        .cta-buttons {
            justify-content: center;
            flex-direction: column;
        }
    }

    @media (max-width: 750px) {
        .content {
            flex-direction: column;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            justify-items: center;

            .top-right-text {
                position: relative;
                top: 0;
                right: 0;
                text-align: center;
            }

            .main-heading {
                font-size: 3rem;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            }

            .tagline {
                font-size: 1.5rem;
            }
        }
    }
</style>
