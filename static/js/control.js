document.addEventListener("DOMContentLoaded", () => {
    console.debug("[control.js] loaded 20260601-4");

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

    const modalShell = document.querySelector("[data-participant-modal]");
    const modalContent = modalShell?.querySelector(".participant-modal-content");
    const controlMain = document.querySelector("[data-control-main]");
    const resultConfirmMessage =
        "¿Seguro que deseas guardar estas selecciones? Podrás editarlas después, pero verifica bien antes de continuar.";
    let phaseDecisionLastTrigger = null;
    let saveAllResultsInProgress = false;

    if (!modalShell || !modalContent || !controlMain) {
        return;
    }

    const getCompetitionId = () => {
        const screen = document.querySelector(".control-screen[data-competition-id]");
        return screen?.dataset.competitionId || "";
    };

    const getCsrfToken = () => {
        const tokenField = document.querySelector("input[name='csrfmiddlewaretoken']");
        return tokenField?.value || "";
    };

    const showModal = () => {
        modalShell.hidden = false;
        document.body.classList.add("modal-open");
    };

    const closeModal = () => {
        modalShell.hidden = true;
        document.body.classList.remove("modal-open");
    };

    const openPhaseDecisionModal = (modal, trigger = null) => {
        if (!modal) {
            return;
        }
        console.debug("[phase-decision] opening", {
            path: window.location.pathname,
        });
        phaseDecisionLastTrigger = trigger;
        modal.hidden = false;
        modal.classList.add("is-active");
        document.body.classList.add("modal-open");
        requestAnimationFrame(() => {
            modal.querySelector("button[data-phase-decision-close]")?.focus({ preventScroll: true });
        });
    };

    const closePhaseDecisionModal = (modal) => {
        if (!modal) {
            return;
        }
        console.debug("[phase-decision] closing", {
            path: window.location.pathname,
        });
        modal.hidden = true;
        modal.classList.remove("is-active");
        document.body.classList.remove("modal-open");
        if (phaseDecisionLastTrigger && document.body.contains(phaseDecisionLastTrigger)) {
            phaseDecisionLastTrigger.focus({ preventScroll: true });
        }
        phaseDecisionLastTrigger = null;
    };

    const resetPhaseDecisionModal = (modal) => {
        if (!modal) {
            return;
        }
        modal.querySelectorAll("[data-phase-decision-preview], [data-phase-decision-manual-panel]").forEach((panel) => {
            panel.hidden = true;
        });
        modal.querySelectorAll("[data-phase-decision-use-recommendation], [data-phase-decision-manual]").forEach(
            (button) => {
                button.classList.remove("is-selected");
            }
        );
        modal.querySelectorAll("[data-phase-create-action], [data-phase-repechage-soon]").forEach((panel) => {
            panel.hidden = true;
        });
        modal.querySelectorAll("[data-phase-repechage-skip], [data-phase-repechage-open]").forEach((button) => {
            button.classList.remove("is-selected");
        });
    };

    const showPhaseDecisionPanel = (modal, panelSelector, selectedButton) => {
        if (!modal) {
            return;
        }
        modal.querySelectorAll("[data-phase-decision-preview], [data-phase-decision-manual-panel]").forEach((panel) => {
            panel.hidden = true;
        });
        modal.querySelectorAll("[data-phase-decision-use-recommendation], [data-phase-decision-manual]").forEach(
            (button) => {
                button.classList.toggle("is-selected", button === selectedButton);
            }
        );
        const panel = modal.querySelector(panelSelector);
        if (panel) {
            panel.hidden = false;
        }
    };

    const chooseRepechageDecision = (modal, selectedButton, options = {}) => {
        if (!modal) {
            return;
        }
        modal.querySelectorAll("[data-phase-repechage-skip], [data-phase-repechage-open]").forEach((button) => {
            button.classList.toggle("is-selected", button === selectedButton);
        });
        const createAction = modal.querySelector("[data-phase-create-action]");
        const soonPanel = modal.querySelector("[data-phase-repechage-soon]");
        if (createAction) {
            createAction.hidden = !options.allowCreate;
        }
        if (soonPanel) {
            soonPanel.hidden = !options.showSoon;
        }
    };

    const setResultCardState = (card, state) => {
        if (!card) {
            return;
        }
        card.classList.toggle("is-winner", state === "winner");
        card.classList.toggle("is-loser", state === "loser");
        card.classList.toggle("is-pending", state === "pending");
        card.classList.toggle("entry-card--winner", state === "winner");
        card.classList.toggle("entry-card--loser", state === "loser");
        card.classList.toggle("entry-card--pending", state === "pending");

        const status = card.querySelector("[data-result-status]");
        const label = card.querySelector("[data-result-label]");
        if (status && label) {
            const labelKey = `${state}Label`;
            label.textContent = status.dataset[labelKey] || status.dataset.pendingLabel || "Pendiente";
        }

        const selectLabel = card.querySelector("[data-result-select-label]");
        if (selectLabel) {
            const form = card.closest("[data-result-form]");
            if (form?.dataset.resultKind === "battle-qualifiers") {
                selectLabel.textContent = state === "winner" ? "Clasificado" : "Clasificar";
            } else {
                selectLabel.textContent = state === "winner" ? "Ganador" : "Marcar ganador";
            }
        }
    };

    const qualifierCheckboxSelectors = [
        "input[type='checkbox'][name='qualified_entry_ids']",
        "input[type='checkbox'][name='qualified_team_ids']",
    ];
    const qualifierCheckboxSelector = qualifierCheckboxSelectors.join(", ");
    const checkedQualifierInputs = (root) =>
        qualifierCheckboxSelectors.flatMap((selector) => Array.from(root.querySelectorAll(`${selector}:checked`)));

    const updateResultFormState = (form) => {
        const winnerInputs = Array.from(form.querySelectorAll("input[type='radio'][name='winner_team_id']"));
        if (winnerInputs.length) {
            const hasWinner = winnerInputs.some((input) => input.checked);
            winnerInputs.forEach((input) => {
                const state = input.checked ? "winner" : hasWinner ? "loser" : "pending";
                setResultCardState(input.closest("[data-result-card]"), state);
            });
            return;
        }

        const qualifierInputs = Array.from(form.querySelectorAll(qualifierCheckboxSelector));
        if (qualifierInputs.length) {
            const hasSelection = qualifierInputs.some((input) => input.checked);
            qualifierInputs.forEach((input) => {
                const state = input.checked ? "winner" : hasSelection ? "loser" : "pending";
                setResultCardState(input.closest("[data-result-card]"), state);
            });
            const counter = form.querySelector("[data-result-counter]");
            if (counter) {
                const requiredSelections = Number(form.dataset.requiredSelections || "0");
                const selectedCount = qualifierInputs.filter((input) => input.checked).length;
                counter.textContent = `Seleccionados: ${selectedCount} / ${requiredSelections}`;
            }
        }
    };

    const resultFormLabel = (form) => form.dataset.resultLabel || "Seleccion";

    const resultFormSignature = (form) => {
        const winnerInput = form.querySelector("input[type='radio'][name='winner_team_id']:checked");
        if (winnerInput) {
            return `winner:${winnerInput.value}`;
        }

        const qualifiedIds = checkedQualifierInputs(form)
            .map((input) => input.value)
            .sort();
        return `qualified:${qualifiedIds.join(",")}`;
    };

    const resultFormChanged = (form) =>
        form.dataset.resultDirty === "true" || resultFormSignature(form) !== (form.dataset.initialResultSignature || "");

    const validateResultForm = (form) => {
        const label = resultFormLabel(form);
        const requiredSelections = Number(form.dataset.requiredSelections || "1");
        const winnerInputs = Array.from(form.querySelectorAll("input[type='radio'][name='winner_team_id']"));
        if (winnerInputs.length) {
            return winnerInputs.some((input) => input.checked)
                ? ""
                : `${label}: selecciona un ganador antes de guardar.`;
        }

        const selectedCount = checkedQualifierInputs(form).length;
        if (!selectedCount) {
            return `${label}: selecciona al menos un clasificado antes de guardar.`;
        }
        if (requiredSelections && selectedCount !== requiredSelections) {
            return `${label}: selecciona ${requiredSelections} clasificado(s); ahora hay ${selectedCount}.`;
        }
        return "";
    };

    const visibleResultForms = () =>
        Array.from(document.querySelectorAll("[data-result-form]")).filter(
            (form) => !form.closest("[hidden]") && resultFormChanged(form)
        );

    const getFormActionUrl = (form) => {
        const actionGetter = Object.getOwnPropertyDescriptor(HTMLFormElement.prototype, "action")?.get;
        const nativeAction = actionGetter ? actionGetter.call(form) : "";
        return nativeAction || window.location.href;
    };

    const saveResultForm = async (form, options = {}) => {
        const csrfToken = getCsrfToken();
        const label = resultFormLabel(form);
        const actionUrl = getFormActionUrl(form);
        const formData = new FormData(form);
        if (options.manualOverride) {
            formData.set("manual_override", "1");
        }
        const response = await fetch(actionUrl, {
            method: (form.method || "POST").toUpperCase(),
            headers: {
                "X-CSRFToken": csrfToken,
                "X-Requested-With": "XMLHttpRequest",
            },
            body: formData,
        });
        const contentType = response.headers.get("content-type") || "";
        let result = { ok: response.ok };
        if (contentType.includes("application/json")) {
            result = await response.json();
        } else {
            const text = await response.text();
            console.error("[control] Respuesta inesperada al guardar resultado", {
                label,
                action: actionUrl,
                status: response.status,
                contentType,
                body: text,
            });
            throw new Error(`${label}: El servidor devolvió una respuesta inesperada. Revisa la consola.`);
        }
        if (result.requires_confirmation) {
            const confirmed = window.confirm(
                result.message ||
                    "Este cambio puede afectar fases posteriores ya iniciadas. ¿Deseas aplicar la corrección manual?"
            );
            if (!confirmed) {
                return { ok: false, canceled: true };
            }
            return saveResultForm(form, { manualOverride: true });
        }
        if (!response.ok || result.ok === false) {
            throw new Error(`${label}: ${result.message || "No fue posible guardar esta seleccion."}`);
        }
        form.dataset.initialResultSignature = resultFormSignature(form);
        form.dataset.resultDirty = "false";
        return result;
    };

    const saveAllButtons = () => Array.from(document.querySelectorAll("[data-save-all-results]"));

    const setSaveAllButtonsSaving = (isSaving) => {
        saveAllButtons().forEach((saveButton) => {
            if (!saveButton.dataset.saveAllOriginalText) {
                saveButton.dataset.saveAllOriginalText = saveButton.textContent.trim();
            }
            saveButton.disabled = isSaving;
            saveButton.textContent = isSaving ? "Guardando..." : saveButton.dataset.saveAllOriginalText;
        });
    };

    const renderParticipantModal = (payload) => {
        const participant = payload.participant;

        modalContent.innerHTML = `
            <header class="participant-modal-header">
                <p class="eyebrow">Participante</p>
                <h2 id="participant-modal-title">${participant.robot_name}</h2>
                <p class="muted-text">${participant.institution_name}</p>
            </header>

            <section class="participant-summary-grid">
                <article class="card participant-summary-card">
                    <p class="eyebrow">Grupo actual</p>
                    <strong>${participant.group_label}</strong>
                </article>
                <article class="card participant-summary-card">
                    <p class="eyebrow">Fase actual</p>
                    <strong>${participant.phase_label}</strong>
                </article>
                <article class="card participant-summary-card">
                    <p class="eyebrow">Estado</p>
                    <strong>${participant.status_label}</strong>
                </article>
            </section>

            <section class="participant-modal-grid">
                <article class="card">
                    <p class="eyebrow">Historial</p>
                    <h3>Resultados y movimientos</h3>
                    <div class="participant-history-list">
                        ${
                            participant.history.length
                                ? participant.history
                                      .map(
                                          (item) => `
                                    <article class="history-item">
                                        <strong>${item.title}</strong>
                                        <span>${item.stage || "Sin fase"} · ${item.status || "Sin estado"}</span>
                                        <p>${item.description || "Sin detalle adicional"}</p>
                                        <small>${item.created_at}</small>
                                    </article>
                                `
                                      )
                                      .join("")
                                : '<p class="muted-text">Aun no hay historial para este participante.</p>'
                        }
                    </div>
                </article>
            </section>
        `;
    };

    const refreshControlContent = async () => {
        const response = await fetch(window.location.href, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        });
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        const newMain = doc.querySelector("[data-control-main]");
        if (newMain) {
            controlMain.innerHTML = newMain.innerHTML;
            bindDynamicControls();
        }
    };

    const openParticipantModal = async (stateId) => {
        const competitionId = getCompetitionId();
        modalContent.innerHTML = '<div class="participant-modal-loading">Cargando participante...</div>';
        showModal();
        const response = await fetch(`/torneo/control/divisiones/${competitionId}/participantes/${stateId}/`, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        });
        const payload = await response.json();
        if (!payload.ok) {
            modalContent.innerHTML = `<p class="muted-text">${payload.message || "No fue posible cargar el participante."}</p>`;
            return;
        }
        renderParticipantModal(payload);
    };

    const bindTriggers = () => {
        document.querySelectorAll(".participant-trigger[data-participant-state-id]").forEach((element) => {
            if (element.dataset.participantTriggerBound === "true") {
                return;
            }
            element.dataset.participantTriggerBound = "true";
            element.addEventListener("click", (event) => {
                const interactiveTarget = event.target.closest("input, select, option, textarea, button, a");
                if (interactiveTarget && interactiveTarget !== element) {
                    return;
                }
                event.preventDefault();
                openParticipantModal(element.dataset.participantStateId);
            });
        });
    };

    const bindResultControls = () => {
        document.querySelectorAll("[data-result-form]").forEach((form) => {
            updateResultFormState(form);
            if (form.dataset.resultFormBound === "true") {
                return;
            }
            form.dataset.resultFormBound = "true";
            form.dataset.initialResultSignature = resultFormSignature(form);
            form.dataset.resultDirty = "false";
            form.querySelectorAll("[data-result-select]").forEach((button) => {
                button.addEventListener("click", (event) => {
                    event.preventDefault();
                    event.stopPropagation();

                    const card = button.closest("[data-result-card]");
                    const input = card?.querySelector(
                        "input[name='qualified_entry_ids'], input[name='qualified_team_ids'], input[name='winner_team_id']"
                    );
                    if (!input) {
                        return;
                    }

                    if (input.type === "checkbox") {
                        input.checked = !input.checked;
                    } else {
                        input.checked = true;
                    }
                    input.dispatchEvent(new Event("change", { bubbles: true }));
                });
            });
            form.addEventListener("change", (event) => {
                if (
                    event.target.matches(
                        "input[name='qualified_entry_ids'], input[name='qualified_team_ids'], input[name='winner_team_id']"
                    )
                ) {
                    form.dataset.resultDirty =
                        resultFormSignature(form) !== (form.dataset.initialResultSignature || "") ? "true" : "false";
                    updateResultFormState(form);
                }
            });
            form.addEventListener("submit", async (event) => {
                event.preventDefault();
                const validationError = validateResultForm(form);
                if (validationError) {
                    alert(validationError);
                    return;
                }
                if (!window.confirm(resultConfirmMessage)) {
                    return;
                }

                const submitButton = form.querySelector("button[type='submit']");
                const originalText = submitButton?.textContent || "";
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.textContent = "Guardando...";
                }
                try {
                    const result = await saveResultForm(form);
                    if (result.canceled) {
                        return;
                    }
                    await refreshControlContent();
                    alert(result.message || `${resultFormLabel(form)} guardado.`);
                } catch (error) {
                    alert(error.message || "No fue posible guardar esta seleccion.");
                } finally {
                    if (submitButton && document.body.contains(submitButton)) {
                        submitButton.disabled = false;
                        submitButton.textContent = originalText;
                    }
                }
            });
        });

        saveAllButtons().forEach((button) => {
            if (button.dataset.saveAllBound === "true") {
                return;
            }
            button.dataset.saveAllBound = "true";
            button.addEventListener("click", async () => {
                if (saveAllResultsInProgress) {
                    return;
                }
                const forms = visibleResultForms();
                if (!forms.length) {
                    alert("No hay cambios nuevos para guardar.");
                    return;
                }

                const validationErrors = forms.map(validateResultForm).filter(Boolean);
                if (validationErrors.length) {
                    alert(validationErrors.join("\n"));
                    return;
                }
                if (!window.confirm(resultConfirmMessage)) {
                    return;
                }

                saveAllResultsInProgress = true;
                setSaveAllButtonsSaving(true);
                try {
                    const savedLabels = [];
                    for (const form of forms) {
                        const result = await saveResultForm(form);
                        if (result.canceled) {
                            break;
                        }
                        savedLabels.push(resultFormLabel(form));
                    }
                    if (!savedLabels.length) {
                        return;
                    }
                    await refreshControlContent();
                    alert(`Selecciones guardadas: ${savedLabels.join(", ")}. Puedes editarlas despues si necesitas corregir.`);
                } catch (error) {
                    alert(error.message || "No fue posible guardar todas las selecciones.");
                } finally {
                    saveAllResultsInProgress = false;
                    setSaveAllButtonsSaving(false);
                }
            });
        });
    };

    const balancedSizes = (total, groupCount) => {
        const base = Math.floor(total / groupCount);
        const remainder = total % groupCount;
        return Array.from({ length: groupCount }, (_item, index) => base + (index < remainder ? 1 : 0));
    };

    const manualPhaseName = (operation, groupSizes) => {
        const firstSize = groupSizes[0] || 0;
        if (operation === "repechage") {
            if (firstSize === 2) {
                return "Repechaje de duelos";
            }
            if (firstSize === 3) {
                return "Repechaje de trios";
            }
            return "Repechaje grupal";
        }
        if (firstSize === 2) {
            return "Ronda de duelos";
        }
        if (firstSize === 3) {
            return "Fase de trios";
        }
        return firstSize ? `Ronda grupal de ${firstSize}` : "Ronda grupal manual";
    };

    const updateManualPhaseForm = (form) => {
        const operation = form.querySelector("[data-manual-operation]:checked")?.value || "normal";
        const total = Number(operation === "repechage" ? form.dataset.repechageCount : form.dataset.normalCount) || 0;
        const distribution = form.querySelector("[data-manual-distribution]");
        const customWrap = form.querySelector("[data-manual-custom-groups]");
        const customInput = form.querySelector("[data-manual-custom-group-count]");
        const qualifiersInput = form.querySelector("[data-manual-qualifiers]");
        const nameInput = form.querySelector("[data-manual-phase-name]");
        const warning = form.querySelector("[data-manual-balanced-warning]");
        const submitButton = form.querySelector("button[type='submit']");

        if (!distribution || !qualifiersInput) {
            return;
        }

        const options = Array.from(distribution.options);
        options.forEach((option) => {
            const matches = option.dataset.operation === operation;
            option.hidden = !matches;
            option.disabled = !matches;
        });
        if (!distribution.selectedOptions.length || distribution.selectedOptions[0].disabled) {
            const firstAvailable = options.find((option) => !option.disabled);
            if (firstAvailable) {
                distribution.value = firstAvailable.value;
            }
        }

        const isCustom = distribution.value === "custom";
        if (customWrap) {
            customWrap.hidden = !isCustom;
        }
        if (customInput) {
            customInput.max = String(Math.max(total, 1));
            if (Number(customInput.value || "0") < 1) {
                customInput.value = "1";
            }
            if (Number(customInput.value || "0") > total && total > 0) {
                customInput.value = String(total);
            }
        }

        let groupSizes = [];
        if (isCustom) {
            const groupCount = Math.max(1, Math.min(Number(customInput?.value || "1"), Math.max(total, 1)));
            groupSizes = total ? balancedSizes(total, groupCount) : [];
        } else {
            const selected = distribution.selectedOptions[0];
            const groupCount = Number(selected?.dataset.groupCount || "0");
            const groupSize = Number(selected?.dataset.groupSize || "0");
            groupSizes = groupCount && groupSize ? Array.from({ length: groupCount }, () => groupSize) : [];
        }

        const groupCount = groupSizes.length;
        const minSize = groupSizes.length ? Math.min(...groupSizes) : 0;
        const maxQualifiers = Math.max(minSize - 1, 0);
        qualifiersInput.max = String(maxQualifiers || 1);
        if (Number(qualifiersInput.value || "0") < 1) {
            qualifiersInput.value = "1";
        }
        if (maxQualifiers && Number(qualifiersInput.value || "0") > maxQualifiers) {
            qualifiersInput.value = String(maxQualifiers);
        }
        const qualifiersPerGroup = Number(qualifiersInput.value || "0");
        const totalQualifiers = qualifiersPerGroup * groupCount;

        const participantsNode = form.querySelector("[data-manual-summary-participants]");
        const groupsNode = form.querySelector("[data-manual-summary-groups]");
        const qualifiersNode = form.querySelector("[data-manual-summary-qualifiers]");
        const eliminatedNode = form.querySelector("[data-manual-summary-eliminated]");
        if (participantsNode) {
            participantsNode.textContent = String(total);
        }
        if (groupsNode) {
            groupsNode.textContent = groupSizes.length ? groupSizes.join(" / ") : "-";
        }
        if (qualifiersNode) {
            qualifiersNode.textContent = groupSizes.length ? String(totalQualifiers) : "-";
        }
        if (eliminatedNode) {
            eliminatedNode.textContent = groupSizes.length ? String(Math.max(total - totalQualifiers, 0)) : "-";
        }
        if (warning) {
            warning.hidden = !isCustom || new Set(groupSizes).size <= 1;
        }
        if (nameInput && (!nameInput.dataset.touched || nameInput.value.trim() === "")) {
            nameInput.value = manualPhaseName(operation, groupSizes);
        }
        if (submitButton) {
            submitButton.disabled = total < 2 || !groupSizes.length || maxQualifiers < 1;
        }
    };

    const bindManualPhaseAssistant = () => {
        document.querySelectorAll("[data-manual-phase-form]").forEach((form) => {
            updateManualPhaseForm(form);
            if (form.dataset.manualPhaseBound === "true") {
                return;
            }
            form.dataset.manualPhaseBound = "true";
            form.querySelectorAll("[data-manual-operation], [data-manual-distribution], [data-manual-custom-group-count], [data-manual-qualifiers]").forEach((input) => {
                input.addEventListener("change", () => updateManualPhaseForm(form));
                input.addEventListener("input", () => updateManualPhaseForm(form));
            });
            const nameInput = form.querySelector("[data-manual-phase-name]");
            if (nameInput) {
                nameInput.addEventListener("input", () => {
                    nameInput.dataset.touched = "true";
                });
            }
        });
    };

    const bindPhaseDecisionModal = () => {
        if (!window.location.pathname.includes("/torneo/control/divisiones/")) {
            return;
        }

        document.querySelectorAll(".control-screen[data-competition-id] [data-phase-decision-modal]").forEach((modal) => {
            if (modal.dataset.phaseDecisionBound === "true") {
                return;
            }
            modal.dataset.phaseDecisionBound = "true";
            modal.hidden = true;
            modal.classList.remove("is-active");
            resetPhaseDecisionModal(modal);
            modal.querySelectorAll("[data-phase-decision-close]").forEach((element) => {
                element.addEventListener("click", () => closePhaseDecisionModal(modal));
            });
            modal.querySelectorAll("[data-phase-decision-cancel]").forEach((element) => {
                element.addEventListener("click", () => closePhaseDecisionModal(modal));
            });
            modal.querySelectorAll("[data-phase-decision-use-recommendation]").forEach((button) => {
                button.addEventListener("click", () => {
                    showPhaseDecisionPanel(modal, "[data-phase-decision-preview]", button);
                });
            });
            modal.querySelectorAll("[data-phase-decision-manual]").forEach((button) => {
                button.addEventListener("click", () => {
                    showPhaseDecisionPanel(modal, "[data-phase-decision-manual-panel]", button);
                });
            });
            modal.querySelectorAll("[data-phase-repechage-skip]").forEach((button) => {
                button.addEventListener("click", () => {
                    chooseRepechageDecision(modal, button, { allowCreate: true });
                });
            });
            modal.querySelectorAll("[data-phase-repechage-open]").forEach((button) => {
                button.addEventListener("click", () => {
                    chooseRepechageDecision(modal, button, { showSoon: true });
                });
            });
        });

        document.querySelectorAll(".control-screen[data-competition-id] button[data-phase-decision-open]").forEach((button) => {
            if (button.dataset.phaseDecisionOpenBound === "true") {
                return;
            }
            button.dataset.phaseDecisionOpenBound = "true";
            console.debug("[phase-decision] registered", {
                text: button.textContent.trim(),
                path: window.location.pathname,
            });
            button.addEventListener("click", (event) => {
                if (event.currentTarget !== button || !button.matches("button[data-phase-decision-open]")) {
                    return;
                }
                event.preventDefault();
                const screen = button.closest(".control-screen[data-competition-id]");
                const modal = screen?.querySelector("[data-phase-decision-modal]");
                if (!modal) {
                    return;
                }
                resetPhaseDecisionModal(modal);
                openPhaseDecisionModal(modal, button);
            });
        });
    };

    const bindDynamicControls = () => {
        bindTriggers();
        bindResultControls();
        bindManualPhaseAssistant();
        bindPhaseDecisionModal();
    };

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") {
            return;
        }
        const phaseDecisionModal = document.querySelector("[data-phase-decision-modal]:not([hidden])");
        if (phaseDecisionModal) {
            closePhaseDecisionModal(phaseDecisionModal);
        }
    });

    modalShell.querySelectorAll("[data-modal-close]").forEach((element) => {
        element.addEventListener("click", closeModal);
    });

    bindDynamicControls();
});
