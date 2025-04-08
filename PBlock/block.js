/**
 * All the actual functionality of the extension; loads as part of the background page.
 *
 * Active ingredient is enable(), which sets up the webRequest callbacks.
 *
 * */

let blockingEnabled = false;
let allFilters = null;
let webRTCPrivacy = null;

function setFilters(newFilters) {
	allFilters = newFilters;
	chrome.storage.local.set({"filters": newFilters});
	if (blockingEnabled) {
		refreshFilters();
	}
}

// Convert URL patterns to declarativeNetRequest rule format
function createRules(filters) {
	return filters.map((filter, index) => ({
		id: index + 1,
		priority: 1,
		action: {
			type: "block"
		},
		condition: {
			urlFilter: filter.replace("*://", "*"),
			resourceTypes: [
				"main_frame", "sub_frame", "stylesheet", "script", "image", 
				"font", "object", "xmlhttprequest", "ping", "media", "websocket"
			]
		}
	}));
}

async function enable(icon = true) {
	if (blockingEnabled) return;
	
	if (allFilters && allFilters.length > 0) {
		const rules = createRules(allFilters);
		await chrome.declarativeNetRequest.updateDynamicRules({
			removeRuleIds: rules.map(rule => rule.id),
			addRules: rules
		});
	}

	blockingEnabled = true;
	if (icon) {
		chrome.action.setIcon({
			path: {
				"16": "enabled16.png",
				"48": "enabled48.png"
			}
		});
	}
}

async function disable(icon = true) {
	if (!blockingEnabled) return;

	const rules = await chrome.declarativeNetRequest.getDynamicRules();
	await chrome.declarativeNetRequest.updateDynamicRules({
		removeRuleIds: rules.map(rule => rule.id),
		addRules: []
	});

	blockingEnabled = false;
	if (icon) {
		chrome.action.setIcon({
			path: {
				"16": "disabled.png",
				"32": "disabled.png"
			}
		});
	}
}

async function refreshFilters() {
	await disable(false);
	await enable(true);
}

async function toggleEnabled() {
	if (blockingEnabled) {
		await disable();
	} else {
		await enable();
	}
}

function setWebRTCPrivacy(flag, store = true) {
	webRTCPrivacy = flag;
	const privacySetting = flag ? "default_public_interface_only" : "default";
	chrome.privacy.network.webRTCIPHandlingPolicy.set({value: privacySetting});
	if (store) {
		chrome.storage.local.set({"webrtc_privacy": flag});
	}
}

// Initialization
chrome.storage.local.get("filters",
	function(result) {
		if (result["filters"] == undefined) {
			console.log("Initializing filters to defaults.");
			setFilters(defaultFilters);
		} else {
			setFilters(result["filters"]);
			allFilters = result["filters"];
		}

		// toggle blocking on-off via the extension icon
		chrome.action.onClicked.addListener(toggleEnabled);
		// initialize blocking
		enable();
	}
);

chrome.storage.local.get("webrtc_privacy",
	function(result) {
		if (result["webrtc_privacy"] == undefined) {
			console.log("Initializing WebRTC privacy to default.");
			setWebRTCPrivacy(false, true);
		} else {
			setWebRTCPrivacy(result["webrtc_privacy"], false);
		}
	}
);
