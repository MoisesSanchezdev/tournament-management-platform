document.addEventListener("DOMContentLoaded", () => {
    const header = document.querySelector(".site-header");
    const hero = document.querySelector(".hero-shell");
    const themeToggles = document.querySelectorAll("[data-theme-toggle]");
    const themeLabels = document.querySelectorAll("[data-theme-label]");
    const themeStorageKey = "preExplotaGlobosTheme";

    const syncViewportWidth = () => {
        document.documentElement.style.setProperty("--app-client-width", `${document.documentElement.clientWidth}px`);
    };

    syncViewportWidth();
    window.addEventListener("resize", syncViewportWidth, { passive: true });
    const setTheme = (theme) => {
        const normalizedTheme = theme === "light" ? "light" : "dark";
        document.documentElement.dataset.theme = normalizedTheme;
        themeLabels.forEach((label) => {
            label.textContent = normalizedTheme === "light" ? "Modo oscuro" : "Modo claro";
        });
        themeToggles.forEach((toggle) => {
            toggle.setAttribute("aria-pressed", normalizedTheme === "light" ? "true" : "false");
            toggle.setAttribute(
                "aria-label",
                normalizedTheme === "light" ? "Cambiar a modo oscuro" : "Cambiar a modo claro"
            );
        });
    };

    const getStoredTheme = () => {
        try {
            return localStorage.getItem(themeStorageKey);
        } catch (error) {
            return null;
        }
    };

    const storeTheme = (theme) => {
        try {
            localStorage.setItem(themeStorageKey, theme);
        } catch (error) {
            return;
        }
    };

    setTheme(getStoredTheme());

    themeToggles.forEach((toggle) => {
        toggle.addEventListener("click", () => {
            const nextTheme = document.documentElement.dataset.theme === "light" ? "dark" : "light";
            storeTheme(nextTheme);
            setTheme(nextTheme);
        });
    });

    const syncHeaderState = () => {
        if (!header) {
            return;
        }
        const isScrolled = window.scrollY > 36;
        header.classList.toggle("is-scrolled", isScrolled);
        document.body.classList.toggle("has-scrolled", isScrolled);
    };

    syncHeaderState();
    window.addEventListener("scroll", syncHeaderState, { passive: true });

    const revealTargets = document.querySelectorAll(
        ".hero-shell, .hero-panel, .page-header, .card, .showcase-card, .rule-card, .sponsor-card, .choice-card, .visual-spotlight, .rules-dashboard__masthead, .rules-dashboard__panel, .home-rules-preview"
    );

    revealTargets.forEach((element, index) => {
        element.classList.add("js-reveal");
        element.style.setProperty("--reveal-delay", `${Math.min(index * 40, 280)}ms`);
    });

    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-visible");
                        observer.unobserve(entry.target);
                    }
                });
            },
            {
                threshold: 0.14,
                rootMargin: "0px 0px -8% 0px",
            }
        );

        revealTargets.forEach((element) => observer.observe(element));
    } else {
        revealTargets.forEach((element) => element.classList.add("is-visible"));
    }

    const countTargets = document.querySelectorAll("[data-count]");
    const animateCount = (element) => {
        const target = Number(element.dataset.count || "0");
        if (!Number.isFinite(target) || target <= 0 || element.dataset.countAnimated === "true") {
            return;
        }

        element.dataset.countAnimated = "true";
        const duration = 900;
        const startTime = performance.now();

        const tick = (now) => {
            const progress = Math.min((now - startTime) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            element.textContent = Math.round(target * eased).toString();
            if (progress < 1) {
                requestAnimationFrame(tick);
            }
        };

        requestAnimationFrame(tick);
    };

    if ("IntersectionObserver" in window) {
        const countObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        animateCount(entry.target);
                        countObserver.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.5 }
        );
        countTargets.forEach((element) => countObserver.observe(element));
    } else {
        countTargets.forEach(animateCount);
    }
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (hero && window.matchMedia("(pointer: fine)").matches && !prefersReducedMotion.matches) {
        const handleHeroMove = (event) => {
            const rect = hero.getBoundingClientRect();
            const offsetX = ((event.clientX - rect.left) / rect.width - 0.5) * 2;
            const offsetY = ((event.clientY - rect.top) / rect.height - 0.5) * 2;

            hero.style.setProperty("--hero-pointer-x", offsetX.toFixed(3));
            hero.style.setProperty("--hero-pointer-y", offsetY.toFixed(3));
        };

        const resetHeroMove = () => {
            hero.style.setProperty("--hero-pointer-x", "0");
            hero.style.setProperty("--hero-pointer-y", "0");
        };

        hero.addEventListener("mousemove", handleHeroMove);
        hero.addEventListener("mouseleave", resetHeroMove);
    }
});
