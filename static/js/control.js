document.addEventListener("DOMContentLoaded", () => {
    const modalShell = document.querySelector("[data-participant-modal]");
    const modalContent = modalShell?.querySelector(".participant-modal-content");
    const controlMain = document.querySelector("[data-control-main]");
    const resultConfirmMessage =
        "¿Seguro que deseas guardar estas selecciones? Podrás editarlas después, pero verifica bien antes de continuar.";

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

    const buildOptions = (items, selectedValue, placeholder) => {
        const options = [`<option value="">${placeholder}</option>`];
        items.forEach((item) => {
            const selected = String(selectedValue || "") === String(item.value) ? "selected" : "";
            options.push(`<option value="${item.value}" ${selected}>${item.label}</option>`);
        });
        return options.join("");
    };

    const battleOptionsByStage = (battles, stageValue) =>
        battles.filter((battle) => battle.stage === stageValue);

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
            selectLabel.textContent = state === "winner" ? "Ganador" : "Marcar ganador";
        }
    };

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

        const qualifierInputs = Array.from(
            form.querySelectorAll("input[type='checkbox'][name='qualified_entry_ids']")
        );
        if (qualifierInputs.length) {
            const hasSelection = qualifierInputs.some((input) => input.checked);
            qualifierInputs.forEach((input) => {
                const state = input.checked ? "winner" : hasSelection ? "loser" : "pending";
                setResultCardState(input.closest("[data-result-card]"), state);
            });
        }
    };

    const resultFormLabel = (form) => form.dataset.resultLabel || "Seleccion";

    const resultFormSignature = (form) => {
        const winnerInput = form.querySelector("input[type='radio'][name='winner_team_id']:checked");
        if (winnerInput) {
            return `winner:${winnerInput.value}`;
        }

        const qualifiedIds = Array.from(
            form.querySelectorAll("input[type='checkbox'][name='qualified_entry_ids']:checked")
        )
            .map((input) => input.value)
            .sort();
        return `qualified:${qualifiedIds.join(",")}`;
    };

    const resultFormChanged = (form) => resultFormSignature(form) !== (form.dataset.initialResultSignature || "");

    const validateResultForm = (form) => {
        const label = resultFormLabel(form);
        const requiredSelections = Number(form.dataset.requiredSelections || "1");
        const winnerInputs = Array.from(form.querySelectorAll("input[type='radio'][name='winner_team_id']"));
        if (winnerInputs.length) {
            return winnerInputs.some((input) => input.checked)
                ? ""
                : `${label}: selecciona un ganador antes de guardar.`;
        }

        const selectedCount = form.querySelectorAll("input[type='checkbox'][name='qualified_entry_ids']:checked").length;
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
        console.debug("[control] Guardando resultado", { label, action: actionUrl });
        const response = await fetch(actionUrl, {
            method: (form.method || "POST").toUpperCase(),
            headers: {
                "X-CSRFToken": csrfToken,
                "X-Requested-With": "XMLHttpRequest",
            },
            body: formData,
        });
        console.debug("[control] Respuesta guardado resultado", {
            label,
            action: actionUrl,
            status: response.status,
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
        return result;
    };

    const renderParticipantModal = (payload) => {
        const participant = payload.participant;
        const battleOptions = battleOptionsByStage(participant.battles, participant.current_stage);

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

            <section class="grid two participant-modal-grid">
                <article class="card">
                    <p class="eyebrow">Edicion rapida</p>
                    <h3>Control manual</h3>
                    <form class="participant-modal-form" data-state-id="${participant.state_id}">
                        <div class="field">
                            <label for="modal_target_stage">Mover a fase</label>
                            <select id="modal_target_stage" name="target_stage">
                                ${buildOptions(participant.stages, participant.current_stage, "Selecciona fase")}
                            </select>
                        </div>

                        <div class="field">
                            <label for="modal_target_group">Mover a grupo</label>
                            <select id="modal_target_group" name="target_group_id">
                                ${buildOptions(participant.groups, participant.current_group_id, "Sin cambio")}
                            </select>
                        </div>

                        <div class="field">
                            <label for="modal_target_battle">Mover a batalla</label>
                            <select id="modal_target_battle" name="target_battle_id">
                                ${buildOptions(battleOptions, participant.current_battle_id, "Asignacion automatica")}
                            </select>
                        </div>

                        <div class="field">
                            <label for="modal_target_status">Estado manual</label>
                            <select id="modal_target_status" name="target_status_override">
                                ${buildOptions(participant.statuses, participant.current_status, "Automatico del sistema")}
                            </select>
                        </div>

                        <div class="field">
                            <label for="modal_note">Nota</label>
                            <textarea id="modal_note" name="note" rows="3" placeholder="Ej. reintegrado por decision de jueces">${participant.notes || ""}</textarea>
                        </div>

                        <div class="form-actions">
                            <button class="button primary" type="submit">Guardar cambios</button>
                        </div>
                    </form>
                </article>

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

        const stageSelect = modalContent.querySelector("#modal_target_stage");
        const battleSelect = modalContent.querySelector("#modal_target_battle");
        if (stageSelect && battleSelect) {
            stageSelect.addEventListener("change", () => {
                const filteredBattles = battleOptionsByStage(participant.battles, stageSelect.value);
                battleSelect.innerHTML = buildOptions(filteredBattles, "", "Asignacion automatica");
            });
        }

        const form = modalContent.querySelector(".participant-modal-form");
        if (form) {
            form.addEventListener("submit", async (event) => {
                event.preventDefault();
                const stateId = form.dataset.stateId;
                const competitionId = getCompetitionId();
                const csrfToken = getCsrfToken();
                const formData = new FormData(form);
                const response = await fetch(
                    `/torneo/control/divisiones/${competitionId}/participantes/${stateId}/actualizar/`,
                    {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": csrfToken,
                            "X-Requested-With": "XMLHttpRequest",
                        },
                        body: formData,
                    }
                );
                const result = await response.json();
                if (!result.ok) {
                    alert(result.message || "No fue posible actualizar el participante.");
                    return;
                }
                await refreshControlContent();
                closeModal();
            });
        }
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
            form.dataset.initialResultSignature = resultFormSignature(form);
            if (form.dataset.resultFormBound === "true") {
                return;
            }
            form.dataset.resultFormBound = "true";
            form.querySelectorAll("[data-result-select]").forEach((button) => {
                button.addEventListener("click", (event) => {
                    event.preventDefault();
                    event.stopPropagation();

                    const card = button.closest("[data-result-card]");
                    const input = card?.querySelector("input[name='qualified_entry_ids'], input[name='winner_team_id']");
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
                if (event.target.matches("input[name='qualified_entry_ids'], input[name='winner_team_id']")) {
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

        document.querySelectorAll("[data-save-all-results]").forEach((button) => {
            if (button.dataset.saveAllBound === "true") {
                return;
            }
            button.dataset.saveAllBound = "true";
            button.addEventListener("click", async () => {
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

                const originalText = button.textContent;
                button.disabled = true;
                button.textContent = "Guardando...";
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
                    if (document.body.contains(button)) {
                        button.disabled = false;
                        button.textContent = originalText;
                    }
                }
            });
        });
    };

    const bindDynamicControls = () => {
        bindTriggers();
        bindResultControls();
    };

    modalShell.querySelectorAll("[data-modal-close]").forEach((element) => {
        element.addEventListener("click", closeModal);
    });

    bindDynamicControls();
});
