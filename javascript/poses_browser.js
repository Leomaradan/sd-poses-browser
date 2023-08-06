const posesBrowser = () => {
    const generateImage = async (poses_browser_image) => {
        const canvas = document.createElement("canvas")
        const image = document.createElement("img")
        image.src = poses_browser_image.src

        await image.decode()

        canvas.width = image.width
        canvas.height = image.height

        canvas.getContext("2d").drawImage(image, 0, 0)

        return canvas.toDataURL()
    }

    const enable = (tabName, controlnetNum) => {
        const input = gradioApp().querySelector(`#${tabName}_controlnet_ControlNet-${controlnetNum}_controlnet_enable_checkbox input`);
        if (input && input.checked === false) {
            input.click()
        }
    }

    const disable = (tabName, controlnetNum) => {
        const input = gradioApp().querySelector(`#${tabName}_controlnet_ControlNet-${controlnetNum}_controlnet_enable_checkbox input`);
        if (input && input.checked === true) {
            input.click()
        }
    }

    const setModel = (tabName, controlnetNum, model) => {
        // Currently not working
        /*
        const input = gradioApp().querySelector(`#${tabName}_controlnet_ControlNet-${controlnetNum}_controlnet_model_dropdown input`);
        if (input && input.value !== model) {
            input.value = model;
            updateInput(input);
        }
        */
    }

    const clearImage = (input) => {
        try {
            if (input.previousElementSibling &&
                input.previousElementSibling.previousElementSibling &&
                input.previousElementSibling.previousElementSibling.querySelector("button[aria-label='Clear']")) {
                input.previousElementSibling.previousElementSibling.querySelector("button[aria-label='Clear']").click()
            }
        } catch (e) {
            console.error(e)
        }
    }

    const setImage = (input, list) => {
        clearImage(input);
        input.value = "";
        input.files = list;
        const event = new Event("change", { "bubbles": true, "composed": true });
        input.dispatchEvent(event);
    }

    const controlNetUnits = (tabName) => {
        return gradioApp().getElementById(tabName + "_#txt2img_controlnet .cnet-unit-tab").length
    }

    const prepareImage = async (image, controlnetNum) => {

        const dataURL = await generateImage(image)
        const blob = await (await fetch(dataURL)).blob()
        const dt = new DataTransfer()
        dt.items.add(new File([blob], `PoseBrowser${controlnetNum}.png`, { type: blob.type }))
        const list = dt.files

        return list;
    }

    const getControlNet = (tabName) => {
        const controlnet = gradioApp().getElementById(tabName + "_controlnet");

        const accordion = controlnet.querySelector(".gradio-accordion .label-wrap")
        if (!accordion.classList.contains("open")) {
            accordion.click();
        }

        return controlnet;
    }

    const goToControlNetTab = (tabName, controlnetNum) => {
        const controlnet = getControlNet(tabName);

        const tabs = controlnet.querySelectorAll("div.tab-nav > button");

        if (tabs !== null && tabs.length > 1) {
            tabs[controlnetNum].click();
        }
    }

    const getControlNetInputs = (tabName, controlnetNum) => {

        return new Promise((resolve) => {

            const controlnet = getControlNet(tabName);

            goToControlNetTab(tabName, controlnetNum);

            const input = controlnet.querySelectorAll("input[type='file']")[controlnetNum * 2];

            if (input == null) {
                const callback = (observer) => {
                    input = controlnet.querySelector("input[type='file']");
                    if (input == null) {
                        resolve(null);
                        return;
                    } else {
                        resolve(input);
                        observer.disconnect();
                    }
                }
                const observer = new MutationObserver(callback);
                observer.observe(controlnet, { childList: true });
            } else {
                resolve(input);
            }
        });
    }

    const clearControlnet = async (tabName, controlnetNum) => {
        console.log('Clearing controlnet', tabName, controlnetNum);
        const input = await getControlNetInputs(tabName, controlnetNum);

        if (input == null) {
            return;
        }

        clearImage(input);
        disable(tabName, controlnetNum);
        setModel(tabName, controlnetNum, 'None');
    }

    const sendToControlNet = async (image, tabName, controlnetNum, model) => {
        console.log('Send image to controlnet', tabName, controlnetNum);
        const list = await prepareImage(image, controlnetNum);

        const input = await getControlNetInputs(tabName, controlnetNum);

        if (input == null) {
            return false;
        }

        setImage(input, list);
        enable(tabName, controlnetNum);
        setModel(tabName, controlnetNum, model);

        return true;
    }

    const getImages = () => {
        const pose = gradioApp().querySelector('#poses_browser_pose_image > img')
        const depth = gradioApp().querySelector('#poses_browser_depth_image > img')
        const canny = gradioApp().querySelector('#poses_browser_canny_image > img')

        return { pose, depth, canny }
    }

    return {
        sendToControlNet,
        clearControlnet,
        getImages,
        controlNetUnits,
        goToControlNetTab,
    }
}

const poses_browser = posesBrowser()

const poses_browser_send = async (tabName) => {
    const { pose, depth, canny } = poses_browser.getImages();

    window[`switch_to_${tabName}`]();

    const numberOfTabs = poses_browser.controlNetUnits(tabName);
    if (numberOfTabs !== 0) {

        let tabNum = 0;
        if (pose) {
            await poses_browser.sendToControlNet(pose, tabName, tabNum, 'control_v11p_sd15_openpose [cab727d4]');
            tabNum++;
        }

        if (depth && tabNum < numberOfTabs) {
            await poses_browser.sendToControlNet(depth, tabName, tabNum, 'control_v11f1p_sd15_depth [cfd03158]');
            tabNum++;
        }

        if (canny && tabNum < numberOfTabs) {
            await poses_browser.sendToControlNet(canny, tabName, tabNum, 'control_v11p_sd15_canny [d14c016b]');
            tabNum++;
        }

        for (let i = tabNum; i <= numberOfTabs; i++) {
            await poses_browser.clearControlnet(tabName, i);
        }

        poses_browser.goToControlNetTab(tabName, 0);

    } else {
        if (pose) {
            await poses_browser.sendToControlNet(pose, tabName, 0, 'control_v11p_sd15_openpose [cab727d4]');
        } else if (depth) {
            await poses_browser.sendToControlNet(depth, tabName, 0, 'control_v11f1p_sd15_depth [cfd03158]');
        } else if (canny) {
            await poses_browser.sendToControlNet(canny, tabName, 0, 'control_v11p_sd15_canny [d14c016b]');

        }
    }
}

async function poses_browser_send_txt2img() {
    poses_browser_send('txt2img');
}

async function poses_browser_send_img2img() {
    poses_browser_send('img2img');
}

const poses_browser_filter = (tag) => {
    const searchTextarea = gradioApp().querySelector('#poses_browser_search textarea');

    searchTextarea.value = tag;
    updateInput(searchTextarea);
}
