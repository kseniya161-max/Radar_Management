document.addEventListener("DOMContentLoaded", () => {

    // === AI SCORE ===
    const btnAiScore = document.getElementById("btn-ai-score");
    if (btnAiScore) {
        btnAiScore.addEventListener("click", async () => {
            btnAiScore.disabled = true;
            btnAiScore.textContent = "AI анализирует...";

            try {
                const response = await fetch("/companies/ai_score_all", {
                    method: "POST"
                });

                if (!response.ok) {
                    throw new Error("Не удалось запустить AI scoring");
                }

                const data = await response.json();
                const taskId = data.task_id;

                const checkStatus = async () => {
                    const statusResponse = await fetch(`/tasks/${taskId}`);

                    if (!statusResponse.ok) {
                        throw new Error("Не удалось получить статус задачи");
                    }

                    const statusData = await statusResponse.json();

                    if (statusData.status === "SUCCESS") {
                        location.reload();
                        return;
                    }

                    if (
                        statusData.status === "FAILURE" ||
                        statusData.status === "REVOKED"
                    ) {
                        throw new Error("AI scoring завершился с ошибкой");
                    }

                    setTimeout(checkStatus, 1000);
                };

                checkStatus();

            } catch (error) {
                alert(error.message);
                btnAiScore.disabled = false;
                btnAiScore.textContent = "AI Score";
            }
        });
    }


    // === RANK BUTTON ===
    const btnRank = document.getElementById("btn-rank");
    if (btnRank) {
        btnRank.addEventListener("click", () => {
            window.location.href = "/web/ranked";
        });
    }


    // === ARCHIVE BUTTON (одиночная) ===
    document.querySelectorAll(".archive-button").forEach(button => {
        button.addEventListener("click", async () => {
            const inn = button.dataset.inn;
            try {
                const response = await fetch(`/companies/${inn}/archive`, {
                    method: "POST"
                });
                if (!response.ok) {
                    throw new Error("Не удалось архивировать компанию");
                }
                location.reload();
            } catch (error) {
                alert(error.message);
            }
        });
    });


    // === RESTORE BUTTON (одиночная) ===
    document.querySelectorAll(".restore-button").forEach(button => {
        button.addEventListener("click", async () => {
            const inn = button.dataset.inn;
            try {
                const response = await fetch(`/companies/${inn}/restore`, {
                    method: "POST"
                });
                if (!response.ok) {
                    throw new Error("Не удалось вернуть компанию из архива");
                }
                location.reload();
            } catch (error) {
                alert(error.message);
            }
        });
    });


    // === BULK PANEL ===
    const bulkPanel = document.getElementById("bulk-panel");
    if (bulkPanel) {
        const bulkCount = document.getElementById("bulk-count");
        const selectAll = document.getElementById("select-all");
        const rowCheckboxes = document.querySelectorAll(".row-checkbox");

        function updateBulkPanel() {
    const checked = document.querySelectorAll(".row-checkbox:checked");
    bulkCount.textContent = checked.length;

    bulkPanel.querySelectorAll("button").forEach(btn => {
        btn.disabled = checked.length === 0;
    });
}

        if (selectAll) {
            selectAll.addEventListener("change", () => {
                rowCheckboxes.forEach(cb => { cb.checked = selectAll.checked; });
                updateBulkPanel();
            });
        }

        rowCheckboxes.forEach(cb => {
            cb.addEventListener("change", updateBulkPanel);
        });
        updateBulkPanel();

            // === BULK EXPORT ===
    const bulkExport = document.getElementById("bulk-export");
    if (bulkExport) {
        bulkExport.addEventListener("click", async () => {
            const inns = Array.from(
                document.querySelectorAll(".row-checkbox:checked")
            ).map(cb => cb.dataset.inn);

            if (inns.length === 0) {
    alert("Выберите компании для экспорта");
    return;
}

            try {
                const response = await fetch("/companies/export", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ inns: inns })
                });

                if (!response.ok) {
                    throw new Error("Не удалось выгрузить компании");
                }

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.href = url;
                link.download = "companies.csv";
                document.body.appendChild(link);
                link.click();
                link.remove();
                URL.revokeObjectURL(url);
            } catch (error) {
                alert(error.message);
            }
        });
    }


        // === BULK ARCHIVE ===
        const bulkArchive = document.getElementById("bulk-archive");
        if (bulkArchive) {
            bulkArchive.addEventListener("click", async () => {
                const inns = Array.from(
                    document.querySelectorAll(".row-checkbox:checked")
                ).map(cb => cb.dataset.inn);

                if (inns.length === 0) return;

                try {
                    const response = await fetch("/companies/bulk/archive", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ inns: inns })
                    });

                    if (!response.ok) {
                        throw new Error("Не удалось архивировать компании");
                    }

                    location.reload();
                } catch (error) {
                    alert(error.message);
                }
            });
        }


        // === BULK RESTORE ===
        const bulkRestore = document.getElementById("bulk-restore");
        if (bulkRestore) {
            bulkRestore.addEventListener("click", async () => {
                const inns = Array.from(
                    document.querySelectorAll(".row-checkbox:checked")
                ).map(cb => cb.dataset.inn);

                if (inns.length === 0) return;

                try {
                    const response = await fetch("/companies/bulk/restore", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ inns: inns })
                    });

                    if (!response.ok) {
                        throw new Error("Не удалось вернуть компании из архива");
                    }

                    location.reload();
                } catch (error) {
                    alert(error.message);
                }
            });
        }


        // === BULK DELETE ===
        const bulkDelete = document.getElementById("bulk-delete");
        if (bulkDelete) {
            bulkDelete.addEventListener("click", async () => {
                const inns = Array.from(
                    document.querySelectorAll(".row-checkbox:checked")
                ).map(cb => cb.dataset.inn);

                if (inns.length === 0) return;

                const confirmed = confirm(
                    `Удалить ${inns.length} компаний? Это действие нельзя отменить.`
                );

                if (!confirmed) return;

                try {
                    const response = await fetch("/companies/bulk/delete", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ inns: inns })
                    });

                    if (!response.ok) {
                        throw new Error("Не удалось удалить компании");
                    }

                    location.reload();
                } catch (error) {
                    alert(error.message);
                }
            });
        }
    }


    // === SYNC SCROLLBAR ===
    const topScrollbar = document.getElementById("top-scrollbar");
    const tableWrapper = document.querySelector(".table-wrapper");

    if (topScrollbar && tableWrapper) {
        let lastTop = -1;
        let lastTable = -1;

        topScrollbar.addEventListener("scroll", () => {
            if (topScrollbar.scrollLeft === lastTable) return;
            lastTop = topScrollbar.scrollLeft;
            tableWrapper.scrollLeft = topScrollbar.scrollLeft;
            lastTable = topScrollbar.scrollLeft;
        });

        tableWrapper.addEventListener("scroll", () => {
            if (tableWrapper.scrollLeft === lastTop) return;
            lastTable = tableWrapper.scrollLeft;
            topScrollbar.scrollLeft = tableWrapper.scrollLeft;
            lastTop = tableWrapper.scrollLeft;
        });
    }

});