/**
 * Director5 shared javascript library
 */

const version = "v1.0.0"; // Follow https://semver.org/

class DirectorLibError extends Error {
	constructor(message = "", module = "Unspecified") {
		super(`${message} | module: ${module}`);
	}
}

class Director {
	static getVersion() {
		return version;
	}
}

Director.UI = class {
	static getComponentTemplate(name) {
		const componentTemplatesElement = document.getElementById("component-templates");
		const templates = componentTemplatesElement.content.querySelectorAll(`.${name}`);

		if (templates.length === 0) {
			throw new DirectorLibError(`Couldn't find template named: ${name}`, Director.UI.name);
		}

		return templates[0];
	}

	static createDialog(title, body, acceptText = "Continue", rejectText = "Nevermind") {
		return new Promise((resolve) => {
			const dialogElem = Director.UI.getComponentTemplate("nc-dialog").cloneNode(true);
			const titleElem = dialogElem.querySelector(".nc-title-text");
			const bodyElem = dialogElem.querySelector(".nc-body-text");
			const acceptButton = dialogElem.querySelector(".nc-accept-button");
			const closeButtons = dialogElem.querySelectorAll(".nc-close-button");

			titleElem.textContent = title;
			bodyElem.innerHTML = body;
			acceptButton.textContent = acceptText;
			closeButtons[1].textContent = rejectText;

			// Transition the dialog
			dialogElem.classList.remove("opacity-0");
			setTimeout(() => {
				dialogElem.classList.add("opacity-100");
			}, 10);

			// Close dialog on esc key press
			const onEscapeKey = (event) => {
				if (event.key === "Escape") closeDialog(false);
			};

			const closeDialog = (result) => {
				dialogElem.classList.remove("opacity-100");
				dialogElem.classList.add("opacity-0");
				setTimeout(() => {
					// Wait for transition to complete
					dialogElem.remove();
				}, 200);
				document.removeEventListener("keydown", onEscapeKey);
				resolve(result);
			};

			// Event listeners
			document.addEventListener("keydown", onEscapeKey);
			acceptButton.addEventListener("click", () => closeDialog(true));
			for (const btn of closeButtons) {
				btn.addEventListener("click", () => closeDialog(false));
			}

			document.body.appendChild(dialogElem);
		});
	}

	static createSnackbar(message, type = Director.UI.Snackbar.INFO) {
		const snackbarElem = Director.UI.getComponentTemplate("nc-snackbar").cloneNode(true);

		switch (type) {
			case Director.UI.Snackbar.INFO:
				snackbarElem.getElementsByClassName("nc-info-circle")[0].classList.remove("hidden");
				break;
			case Director.UI.Snackbar.ERROR:
				snackbarElem.getElementsByClassName("nc-error-circle")[0].classList.remove("hidden");
				break;
			case Director.UI.Snackbar.WARNING:
				snackbarElem.getElementsByClassName("nc-warning-circle")[0].classList.remove("hidden");
				break;
			case Director.UI.Snackbar.SUCCESS:
				snackbarElem.getElementsByClassName("nc-success-circle")[0].classList.remove("hidden");
				break;
			default:
				throw new DirectorLibError(`Invalid snackbar type passed: ${type}`, Director.UI.name);
		}

		snackbarElem.getElementsByTagName("p")[0].textContent = message;
		document.getElementById("tooltip-holder").appendChild(snackbarElem);
		setTimeout(() => {
			snackbarElem.classList.add("translate-y-0");
		}, 50);

		setTimeout(() => {
			snackbarElem.classList.add("opacity-0");
			setTimeout(() => {
				snackbarElem.remove();
			}, 200);
		}, 8000);
	}
};

Director.UI.Snackbar = class {
	static ERROR = "error";
	static WARNING = "warning";
	static SUCCESS = "success";
	static INFO = "info";
};

document.addEventListener("alpine:init", () => {
	Alpine.directive("tooltip", (el, { expression }, { evaluateLater, effect }) => {
		const getTooltipMessage = evaluateLater(expression);

		effect(() => {
			getTooltipMessage((tooltipMessage) => {
				const tooltipElem = Director.UI.getComponentTemplate("tooltip").cloneNode(true);
				tooltipElem.firstElementChild.textContent = tooltipMessage;
				document.body.appendChild(tooltipElem);
				Alpine.initTree(tooltipElem);

				const instance = Popper.createPopper(el, tooltipElem, {
					placement: "top",
					modifiers: [
						{
							name: "offset",
							options: {
								offset: [0, 8],
							},
						},
					],
				});
				el.addEventListener("mouseenter", () => {
					new Promise((resolve) => {
						instance.update();
						resolve();
					});

					tooltipElem.classList.remove("opacity-0");
					tooltipElem.classList.add("opacity-100");
				});
				el.addEventListener("mouseleave", () => {
					tooltipElem.classList.remove("opacity-100");
					tooltipElem.classList.add("opacity-0");
				});
			});
		});
	});
});
