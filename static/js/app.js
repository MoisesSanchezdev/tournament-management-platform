document.addEventListener("DOMContentLoaded", () => {
    const header = document.querySelector(".site-header");
    const hero = document.querySelector(".hero-shell");
    const themeToggles = document.querySelectorAll("[data-theme-toggle]");
    const themeLabels = document.querySelectorAll("[data-theme-label]");
    const themeStorageKey = "preExplotaGlobosTheme";

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
        ".hero-shell, .page-header, .card, .showcase-card, .rule-card, .sponsor-card, .choice-card, .pdf-frame, .visual-spotlight, .rule-banner"
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

    if (hero && window.matchMedia("(pointer: fine)").matches) {
        const heroLayers = hero.querySelectorAll(".hero-copy, .hero-rail, .hero-orbit");

        const handleHeroMove = (event) => {
            const rect = hero.getBoundingClientRect();
            const offsetX = ((event.clientX - rect.left) / rect.width - 0.5) * 2;
            const offsetY = ((event.clientY - rect.top) / rect.height - 0.5) * 2;

            hero.style.setProperty("--hero-tilt-x", `${offsetX * 5}deg`);
            hero.style.setProperty("--hero-tilt-y", `${offsetY * -5}deg`);

            heroLayers.forEach((layer, index) => {
                const depth = (index + 1) * 7;
                layer.style.transform = `translate3d(${offsetX * depth}px, ${offsetY * depth}px, 0)`;
            });
        };

        const resetHeroMove = () => {
            hero.style.setProperty("--hero-tilt-x", "0deg");
            hero.style.setProperty("--hero-tilt-y", "0deg");
            heroLayers.forEach((layer) => {
                layer.style.transform = "";
            });
        };

        hero.addEventListener("mousemove", handleHeroMove);
        hero.addEventListener("mouseleave", resetHeroMove);
    }
});
