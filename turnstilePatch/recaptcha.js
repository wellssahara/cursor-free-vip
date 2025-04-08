function qSelector(selector) {
    return document.querySelector(selector);
}
 
(function() {
    'use strict';
    var solved = false;
    var checkBoxClicked = false;
    var requestCount = 0;
    const MAX_ATTEMPTS = 1;
    const CHECK_BOX = ".recaptcha-checkbox-border";
    const AUDIO_BUTTON = "#recaptcha-audio-button";
    const PLAY_BUTTON = ".rc-audiochallenge-play-button .rc-button-default";
    const AUDIO_SOURCE = "#audio-source";
    const IMAGE_SELECT = "#rc-imageselect";
    const RESPONSE_FIELD = ".rc-audiochallenge-response-field";
    const AUDIO_ERROR_MESSAGE = ".rc-audiochallenge-error-message";
    const AUDIO_RESPONSE = "#audio-response";
    const RELOAD_BUTTON = "#recaptcha-reload-button";
    const RECAPTCHA_STATUS = "#recaptcha-accessible-status";
    const DOSCAPTCHA = ".rc-doscaptcha-body";
    const VERIFY_BUTTON = "#recaptcha-verify-button";
    var recaptchaInitialStatus = qSelector(RECAPTCHA_STATUS) ? qSelector(RECAPTCHA_STATUS).innerText : ""
    function isHidden(el) {
        return(el.offsetParent === null)
    }
    try {
        if(!checkBoxClicked && qSelector(CHECK_BOX) && !isHidden(qSelector(CHECK_BOX))) {
            //console.log("checkbox clicked");
            qSelector(CHECK_BOX).click();
            checkBoxClicked = true;
        }
        //Check if the captcha is solved
        if(qSelector(RECAPTCHA_STATUS) && (qSelector(RECAPTCHA_STATUS).innerText != recaptchaInitialStatus)) {
            solved = true;
            console.log("SOLVED");
        }
        if(requestCount > MAX_ATTEMPTS) {
            console.log("Attempted Max Retries. Stopping the solver");
            solved = true;
        }
        //Stop solving when Automated queries message is shown
        if(qSelector(DOSCAPTCHA) && qSelector(DOSCAPTCHA).innerText.length > 0) {
            console.log("Automated Queries Detected");
        }
    } catch(err) {
        console.log(err.message);
        console.log("An error occurred while solving. Stopping the solver.");
    }
})();