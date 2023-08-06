let poses_browser_debug = true
let poses_browser_state = "free"

function poses_browser_delay(ms) { return new Promise(resolve => setTimeout(resolve, ms)) }


async function poses_browser_get_image_for_ext(poses_browser_image) {
    if (poses_browser_debug) {
        console.log("poses_browser_get_image_for_ext:start")
    }

    const canvas = document.createElement("canvas")
    const image = document.createElement("img")
    image.src = poses_browser_image.src

    await image.decode()

    canvas.width = image.width
    canvas.height = image.height

    canvas.getContext("2d").drawImage(image, 0, 0)

    if (poses_browser_debug) console.log("poses_browser_get_image_for_ext:end")
    return canvas.toDataURL()
}

async function poses_browser_lock(reason) {
    if (poses_browser_debug) console.log("poses_browser_lock:start")
    // Wait until lock removed
    let i = 0
    while (poses_browser_state != "free") {
        await poses_browser_delay(200)
        i = i + 1
        if (i === 150) {
            throw new Error("Still locked after 30 seconds. Please Reload UI.")
        }
    }
    // Lock
    poses_browser_state = reason
    if (poses_browser_debug) console.log("poses_browser_lock:end")
}

async function poses_browser_unlock() {
    if (poses_browser_debug) console.log("poses_browser_unlock:start")
    poses_browser_state = "free"
    if (poses_browser_debug) console.log("poses_browser_unlock:end")
}

async function poses_browser_gototab(tabname) {
    if (poses_browser_debug) console.log("poses_browser_gototab:start")
    await poses_browser_lock("poses_browser_gototab")

    tabNav = gradioApp().querySelector(".tab-nav")
    const tabNavChildren = tabNav.children
    let tabNavButtonNum
    if (typeof tabname === "number") {
        let buttonCnt = 0
        for (let i = 0; i < tabNavChildren.length; i++) {
            if (tabNavChildren[i].tagName === "BUTTON") {
                if (buttonCnt === tabname) {
                    tabNavButtonNum = i
                    break
                }
                buttonCnt++
            }
        }
    } else {
        for (let i = 0; i < tabNavChildren.length; i++) {
            if (tabNavChildren[i].tagName === "BUTTON" && tabNavChildren[i].textContent.trim() === tabname) {
                tabNavButtonNum = i
                break
            }
        }
    }
    let tabNavButton = tabNavChildren[tabNavButtonNum]
    tabNavButton.click()

    // Wait for click-action to complete
    const startTime = Date.now()
    // 60 seconds in milliseconds
    const timeout = 60000

    await poses_browser_delay(100)
    while (!tabNavButton.classList.contains("selected")) {
        tabNavButton = tabNavChildren[tabNavButtonNum]
        if (Date.now() - startTime > timeout) {
            throw new Error("poses_browser_gototab: 60 seconds have passed")
        }
        await poses_browser_delay(200)
    }

    await poses_browser_unlock()
    if (poses_browser_debug) console.log("poses_browser_gototab:end")
}

function poses_browser_webui_current_tab() {
    if (poses_browser_debug) console.log("poses_browser_webui_current_tab:start")
    const tabs = gradioApp().querySelectorAll("#tabs > [id^='tab_']")
    let id
    for (const element of tabs) {
        if (element.style.display === "block") {
            id = element.id
            break
        }
    }
    if (poses_browser_debug) console.log("poses_browser_webui_current_tab:end")
    return id
}

async function poses_browser_controlnet_send(image, toTabNum, controlnetNum) {
    if (poses_browser_debug) console.log("poses_browser_controlnet_send:start")
    // Logic originally based on github.com/fkunn1326/openpose-editor
    let list = undefined;
    if (image) {
        const dataURL = await poses_browser_get_image_for_ext(image)
        const blob = await (await fetch(dataURL)).blob()
        const dt = new DataTransfer()
        dt.items.add(new File([blob], `PoseBrowser${controlnetNum}.png`, { type: blob.type }))
        list = dt.files
    }

    const model = controlnetNum === 0 ? 'control_v11p_sd15_openpose' : 'control_v11f1p_sd15_depth';

    await poses_browser_gototab(toTabNum)
    const current_tabid = poses_browser_webui_current_tab()
    const current_tab = current_tabid.replace("tab_", "")
    const tab_controlnet = gradioApp().getElementById(current_tab + "_controlnet")
    let accordion = tab_controlnet.querySelector("#controlnet > .label-wrap > .icon")
    if (accordion.style.transform.includes("rotate(90deg)")) {
        accordion.click()
        // Wait for click-action to complete
        const startTime = Date.now()
        // 60 seconds in milliseconds
        const timeout = 60000

        await poses_browser_delay(100)
        while (accordion.style.transform.includes("rotate(90deg)")) {
            accordion = tab_controlnet.querySelector("#controlnet > .label-wrap > .icon")
            if (Date.now() - startTime > timeout) {
                throw new Error("poses_browser_controlnet_send/accordion: 60 seconds have passed")
            }
            await poses_browser_delay(200)
        }
    }

    let inputImage
    let inputContainer

    controlnetType = gradioApp().getElementById(current_tab + "_controlnet_ControlNet_input_image") !== null ? "single" : "multi"

    if (controlnetType == "single") {
        inputImage = gradioApp().getElementById(current_tab + "_controlnet_ControlNet_input_image")
    } else {
        const tabs = gradioApp().getElementById(current_tab + "_controlnet_tabs")
        const tab_num = (parseInt(controlnetNum) + 1).toString()
        tab_button = tabs.querySelector(".tab-nav > button:nth-child(" + tab_num + ")")
        tab_button.click()
        // Wait for click-action to complete
        const startTime = Date.now()
        // 60 seconds in milliseconds
        const timeout = 60000

        await poses_browser_delay(100)
        while (!tab_button.classList.contains("selected")) {
            tab_button = tabs.querySelector(".tab-nav > button:nth-child(" + tab_num + ")")
            if (Date.now() - startTime > timeout) {
                throw new Error("poses_browser_controlnet_send/tabs: 60 seconds have passed")
            }
            await poses_browser_delay(200)
        }
        inputImage = gradioApp().getElementById(current_tab + "_controlnet_ControlNet-" + controlnetNum.toString() + "_input_image")
    }
    try {
        inputContainer = inputImage.querySelector('div[data-testid="image"]')
    } catch (e) { }

    const input = inputContainer.querySelector("input[type='file']")

    let clear
    try {
        clear = inputContainer.querySelector("button[aria-label='Remove Image']")
        if (clear) {
            clear.click()
        }
    } catch (e) {
        console.error(e)
    }

    try {
        // Wait for click-action to complete
        const startTime = Date.now()
        // 60 seconds in milliseconds
        const timeout = 60000
        while (clear) {
            clear = inputContainer.querySelector("button[aria-label='Remove Image']")
            if (Date.now() - startTime > timeout) {
                throw new Error("poses_browser_controlnet_send/clear: 60 seconds have passed")
            }
            await poses_browser_delay(200)
        }
    } catch (e) {
        console.error(e)
    }

    input.value = ""
    input.files = list


    /*const modelDropdown = gradioApp().getElementById(current_tab + "_controlnet_ControlNet-" + controlnetNum.toString() + "_controlnet_model_dropdown");
 
    modelDropdown.querySelector('input').click();
 
    // Wait for click-action to complete
    const startTime = Date.now()
    // 60 seconds in milliseconds
    const timeout = 60000
 
    await poses_browser_delay(100)
    while (!modelDropdown.querySelector("ul")) {
        if (Date.now() - startTime > timeout) {
            throw new Error("poses_browser_controlnet_send/modelDropdown: 60 seconds have passed")
        }
        await poses_browser_delay(200)
    }
 
    modelDropdown.querySelectorAll("li").forEach(li => {
        if (li.innerText.includes(model)) {
            li.click()
        }
    });*/



    const event = new Event("change", { "bubbles": true, "composed": true })
    input.dispatchEvent(event)

    if (poses_browser_debug) console.log("poses_browser_controlnet_send:end")
}

const getImages = () => {
    const pose = gradioApp().querySelector('#poses_browser_pose_image > img')
    const depth = gradioApp().querySelector('#poses_browser_depth_image > img')

    return { pose, depth }
}
//txt2img_controlnet_ControlNet-0_controlnet_enable_checkbox
//txt2img_controlnet_ControlNet-0_controlnet_model_dropdown

async function poses_browser_send_txt2img() {
    const { pose, depth } = getImages();
    await poses_browser_controlnet_send(pose, 0, 0);
    await poses_browser_controlnet_send(depth, 0, 1);

    //poses_browser_controlnet_send(0, tab_base_tag, image_index, controlnetNum, controlnetType)
}

async function poses_browser_send_img2img() {
    const { pose, depth } = getImages();
    //poses_browser_controlnet_send(1, tab_base_tag, image_index, controlnetNum, controlnetType)
    await poses_browser_controlnet_send(pose, 1, 0),
        await poses_browser_controlnet_send(depth, 1, 1);
}

const poses_browser_filter = (tag) => {
    console.log("poses_browser_filter:start")
    console.log({tag});

    const searchTextarea = gradioApp().querySelector('#poses_browser_search textarea');

    searchTextarea.value = tag;
    updateInput(searchTextarea);
}
