// Modified chatbubble.js to work with local FastAPI endpoints
// This version uses relative URLs and includes site parameter detection

(async function () {
  const TOGGLE_CHATWIDGET_ID = 'toggleChatwidget';
  const INITIAL_MESSAGES_POPUP_ID = 'initialMessagesPopup';
  const CLOSE_INITIAL_MESSAGES_POPUP_ID = 'closeInitialMessagesPopup';
  const CHAT_WIDGET_POPUP_SHOWN_KEY = 'chatWidgetPopupShown';
  const CHAT_ICON_ID = 'chatIcon';
  const CHAT_WIDGET_IFRAME_ID = 'chatWidgetIframe';
  const CHATBOT_EMBED_URL = '/chatbot/embed/';
  const GET_CHATWIDGET_DATA_API_URL = '/chatbot/api/chatwidget/';
  const CHAT_WIDGET_Z_INDEX = 9999999;
  const scriptElement = document.currentScript;
  
  // Use relative URLs - no domain needed, will use current origin
  const domain = ''; // Empty string means relative URLs
  const widgetPosition = scriptElement.getAttribute('data-position') || 'right';
  
  // Detect site parameter from current URL
  // If URL is /site/www.example.com, extract 'www.example.com'
  function getSiteParameter() {
    const path = window.location.pathname;
    if (path.startsWith('/site/')) {
      return path.replace('/site/', '').split('/')[0];
    }
    // If not on /site/ path, try to get from referrer or use current hostname
    return window.location.hostname || 'default';
  }
  
  const siteParameter = getSiteParameter();
  const INITIAL_MESSAGES_POPUP_REMOVED_KEY = `initialMessagesPopupRemoved_${siteParameter}`;

  console.log('[Chat Widget] Initializing widget for site:', siteParameter);

  // API call to get some chatbot's/chatwidget's data
  const data = await getChatwidgetData(siteParameter);
  console.log('[Chat Widget] Widget data loaded successfully');

  const iconImg = data.chat_bubble_img;
  const showPopupMessagesOnlyOnce = data.show_popup_messages_only_once;
  const iconClose = data.close;
  const defaultIcon = data.default_icon || false;
  const iconColor = data.chat_bubble_color || '#DAE7FB';
  const iconTextColor = data.user_msg_text_color || '#69707A';
  const initialMessages = Array.isArray(data.initial_messages)
    ? data.initial_messages
    : [];
  const popupType = data.popup_type;
  const initialMessagePopupDelay = data.initial_message_popup_delay;
  const chatwidgetPopupDelay = data.chatwidget_popup_delay;
  const mobilePopupType = data.mobile_popup_type;
  const mobileInitialMessagePopupDelay =
    data.mobile_initial_message_popup_delay;
  const mobileChatwidgetPopupDelay = data.mobile_chatwidget_popup_delay;
  const mobileInitialMessages = data.mobile_initial_messages;
  const initialPopupMessageFontFamily = data.font_family;
  const initialPopupMessageFontSize = data.font_size;
  const widgetSize = data.size_of_widget;
  let isInitialMessagesPopupShowing = false;
  const SMALL_SCREEN_WIDTH = 450;
  const currentScreenWidth = window.innerWidth;
  const isMobileDevice = window.navigator.userAgent.includes('Mobile');
  const isMobileScreen = currentScreenWidth < SMALL_SCREEN_WIDTH;
  const isMobile = isMobileScreen || isMobileDevice;

  // Add the chat bubble styles/CSS to the head of the document
  const styleElement = document.createElement('style');
  styleElement.textContent = getChatbubbleStyles();
  document.head.appendChild(styleElement);

  // Add the chat bubble HTML to the body of the document
  document.body.insertAdjacentHTML(
    'beforeend',
    getChatbubbleHTML(widgetPosition)
  );
  // Create an iframe element for chat widget
  const chatWidget = getChatWidgetIframe(isMobile, widgetPosition);
  document.body.appendChild(chatWidget);

  // Add event listener for the chat bubble click
  document
    .getElementById(TOGGLE_CHATWIDGET_ID)
    .addEventListener('click', toggleChatWidgetIframe);

  if (isMobile) {
    if (mobilePopupType === 'initial_messages_popup') {
      showInitialMessagesPopup(
        mobileInitialMessagePopupDelay,
        mobileInitialMessages
      );
    } else if (mobilePopupType === 'chatwidget_popup') {
      showChatwidgetPopup(mobileChatwidgetPopupDelay);
    }
  } else {
    if (popupType === 'initial_messages_popup') {
      showInitialMessagesPopup(initialMessagePopupDelay, initialMessages);
    } else if (popupType === 'chatwidget_popup') {
      showChatwidgetPopup(chatwidgetPopupDelay);
    }
  }

  /**
   * Returns HTML for the chat icon image.
   */
  function getChatIconImgHTML() {
    if (defaultIcon) {
      return `<img style="display: block; height: 18px; margin: auto;" width="30px" src="${iconImg}" alt="">`;
    }
    return `<img style="width: 58px; height: 58px; border-radius: 50%; background-size: cover; background-position: center; vertical-align: middle;" src="${iconImg}" alt="">`;
  }

  /**
   * Returns HTML for the close icon.
   */
  function getCloseIconHTML() {
    return `<img style="display: block; height: 40px; margin: auto;" width="30px" src="${iconClose}" alt="">`;
  }

  /**
   * Toggle the visibility of the chat widget iframe and update the chat icon accordingly.
   */
  function toggleChatWidgetIframe() {
    if (isInitialMessagesPopupShowing) {
      removeInitialMessagesPopup();
    }

    const CHAT_WIDGET_IFRAME_ID = 'chatWidgetIframe';
    const CHAT_ICON_ID = 'chatIcon';

    const chatWidget = document.getElementById(CHAT_WIDGET_IFRAME_ID);
    const chatIconElement = document.getElementById(CHAT_ICON_ID);

    if (chatWidget.style.visibility === 'hidden') {
      // Show the chat widget
      console.log('[Chat Widget] Opening chat widget');
      // Reapply styles to ensure they're set correctly
      const isNowMobile = window.innerWidth < SMALL_SCREEN_WIDTH;
      if (!isNowMobile) {
        chatWidget.style.borderRadius = '12px 12px 12px 12px';
        chatWidget.style.overflow = 'hidden';
        chatWidget.style.boxShadow = '0 4px 20px rgba(0,0,0,0.15)';
        chatWidget.style.backgroundColor = 'transparent';
      }
      
      chatWidget.style.zIndex = CHAT_WIDGET_Z_INDEX.toString();
      chatWidget.style.visibility = 'visible';
      chatWidget.style.opacity = '1';

      // Remove the current chat icon image
      const chatIconImgToRemove = chatIconElement.querySelector('img');
      chatIconElement?.removeChild(chatIconImgToRemove);
      chatIconElement.innerHTML = getCloseIconHTML();
      if (screen.width < 500) {
        disableBodyScroll();
        hideChatbubble();
      }
    } else {
      // Hide the chat widget
      console.log('[Chat Widget] Closing chat widget');
      chatWidget.style.visibility = 'hidden';
      chatWidget.style.opacity = '0';
      chatWidget.style.zIndex = (-CHAT_WIDGET_Z_INDEX).toString();
      // Remove the close icon
      const closeIconToRemove = chatIconElement.querySelector('img');
      chatIconElement?.removeChild(closeIconToRemove);
      chatIconElement.innerHTML = getChatIconImgHTML();

      if (document.body.hasAttribute('data-scroll-position')) {
        enableBodyScroll();
      }
    }
  }

  window.toggleChatWidgetIframe = toggleChatWidgetIframe;

  /*
   * Returns CSS/Styling for the chat bubble.
   */
  function getChatbubbleStyles() {
    const styles = `
        .chat-bubble {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
            z-index: 999999;
            background-color: ${iconColor};
            color: ${iconTextColor};
            transition: transform 0.1s ease-in;
        }
        /* Add the hover effect */
        .chat-bubble:hover {
            transform: scale(1.1);
        }
        `;
    return styles;
  }

  /**
   * Returns HTML for the chat bubble.
   */
  function getChatbubbleHTML(position = 'right') {
    const chatbubblePosition =
      position === 'left'
        ? 'left: 20px; right: auto;'
        : 'right: 20px; left: auto;';

    return `
        <div id="${TOGGLE_CHATWIDGET_ID}" class="chat-bubble" style="position: fixed !important; bottom: 20px !important; ${chatbubblePosition} z-index: 999999;">
            <div id="chatIcon">
                ${getChatIconImgHTML()}
            </div>
        </div>`;
  }

  function disableBodyScroll() {
    const scrollY = window.scrollY;
    if (scrollY >= 0) {
      document.body.setAttribute('data-scroll-position', scrollY.toString());
    }

    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';

    document.body.style.position = 'fixed';
    document.body.style.top = `-${scrollY}px`;
    document.body.style.width = '100%';

    // Safari specific: Disable touch scrolling by preventing default behavior
    document.addEventListener('touchmove', preventDefault, { passive: false });
  }

  function enableBodyScroll() {
    const scrollY = parseInt(
      document.body.getAttribute('data-scroll-position') || '0'
    );

    document.body.style.overflow = '';
    document.documentElement.style.overflow = '';
    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.width = '';

    if (scrollY > 0 && document.body.hasAttribute('data-scroll-position')) {
      requestAnimationFrame(() => {
        window.scrollTo({
          top: scrollY,
          behavior: 'instant',
        });
      });
    }

    document.body.removeAttribute('data-scroll-position');

    // Remove the touchmove event listener
    document.removeEventListener('touchmove', preventDefault, {
      passive: false,
    });
  }

  function preventDefault(e) {
    e.preventDefault();
  }

  function hideChatbubble() {
    const toggleButton = document.getElementById(TOGGLE_CHATWIDGET_ID);
    toggleButton.style.display = 'none';
  }

  function showChatbubble() {
    const toggleButton = document.getElementById(TOGGLE_CHATWIDGET_ID);
    toggleButton.style.display = 'flex';
  }

  /**
   * Returns an iframe element for the chat widget.
   */
  function getChatWidgetIframe(isMobile = false, position = 'right') {
    const chatWidget = document.createElement('iframe');
    chatWidget.id = CHAT_WIDGET_IFRAME_ID;
    chatWidget.allow = 'microphone';
    chatWidget.style.position = 'fixed';
    chatWidget.style.zIndex = CHAT_WIDGET_Z_INDEX.toString();
    chatWidget.style.border = 'none';
    chatWidget.style.visibility = 'hidden';
    chatWidget.style.opacity = '0';
    chatWidget.style.transition = 'opacity 0.3s ease';
    chatWidget.style.background = 'transparent';

    // Helper function to set styles based on screen size and position
    function setChatWidgetStyles(isMobile) {
      let width, height;

      if (isMobile) {
        width = '100%';
        height = '100%';
        chatWidget.style.top = '0';
        chatWidget.style.left = '0';
        chatWidget.style.right = '0';
        chatWidget.style.bottom = '0';
        chatWidget.style.borderRadius = '0';
      } else {
        if (widgetSize === 'small') {
          width = '350px';
          height = '50%';
        } else if (widgetSize === 'medium') {
          width = '400px';
          height = '65%';
        } else if (widgetSize === 'large') {
          width = '500px';
          height = '80%';
        } else {
          width = '400px';
          height = '65%';
        }

        chatWidget.style.top = 'auto';
        chatWidget.style.bottom = '100px';
        chatWidget.style.borderRadius = '12px 12px 12px 12px';
        chatWidget.style.overflow = 'hidden';
        chatWidget.style.boxShadow = '0 4px 20px rgba(0,0,0,0.15)';
        chatWidget.style.backgroundColor = 'transparent';

        // Position the widget based on the position attribute
        if (position === 'left') {
          chatWidget.style.left = '20px';
          chatWidget.style.right = 'auto';
        } else {
          chatWidget.style.left = 'auto';
          chatWidget.style.right = '20px';
        }
      }

      chatWidget.style.width = width;
      chatWidget.style.height = height;
    }

    // Set initial styles
    setChatWidgetStyles(isMobile);
    
    // Ensure styles are applied after a short delay (in case of timing issues)
    setTimeout(() => {
      if (!isMobile) {
        chatWidget.style.borderRadius = '12px 12px 12px 12px';
        chatWidget.style.overflow = 'hidden';
        chatWidget.style.boxShadow = '0 4px 20px rgba(0,0,0,0.15)';
        chatWidget.style.backgroundColor = 'transparent';
      }
    }, 100);

    // Add resize listener to handle window changes
    window.addEventListener('resize', () => {
      const isNowMobile = window.innerWidth < SMALL_SCREEN_WIDTH;
      setChatWidgetStyles(isNowMobile);
      // Reapply border-radius for desktop
      if (!isNowMobile) {
        chatWidget.style.borderRadius = '12px 12px 12px 12px';
        chatWidget.style.overflow = 'hidden';
      }
    });

    // Include site parameter in iframe URL
    chatWidget.src = `${domain}${CHATBOT_EMBED_URL}${siteParameter}?source=chatbubble`;
    return chatWidget;
  }

  // Listen for the close message from the iframe
  window.addEventListener('message', function (event) {
    if (event.data === 'close-chatbubble') {
      console.log('[Chat Widget] Received close message from iframe');
      const chatWidget = document.getElementById('chatWidgetIframe');
      const chatIconElement = document.getElementById('chatIcon');

      if (chatWidget) {
        chatWidget.style.visibility = 'hidden';
        chatWidget.style.opacity = '0';
        chatWidget.style.zIndex = (-CHAT_WIDGET_Z_INDEX).toString();

        const closeIconToRemove = chatIconElement.querySelector('img');
        if (closeIconToRemove) {
          chatIconElement?.removeChild(closeIconToRemove);
          chatIconElement.innerHTML = getChatIconImgHTML();
        }

        if (document.body.hasAttribute('data-scroll-position')) {
          enableBodyScroll();
        }
        showChatbubble();
      }
    }
  });

  /**
   * Removes the initial messages popup
   */
  function removeInitialMessagesPopup(removePermanently = false) {
    if (isInitialMessagesPopupShowing) {
      console.log('[Chat Widget] Removing initial messages popup');
      isInitialMessagesPopupShowing = false;
      document.getElementById(INITIAL_MESSAGES_POPUP_ID).remove();
      if (removePermanently || showPopupMessagesOnlyOnce) {
        setLocalStorageItem(INITIAL_MESSAGES_POPUP_REMOVED_KEY, true);
      }
    }
  }

  /**
   * Displays the initial messages popup, if needed.
   */
  function showInitialMessagesPopup(delay, initialMessages) {
    // if delay is negative OR local storage item for popup removal is set
    // then don't show the popup.
    if (!showPopupMessagesOnlyOnce) {
      setLocalStorageItem(INITIAL_MESSAGES_POPUP_REMOVED_KEY, '');
    }
    if (
      delay < 0 ||
      getLocalStorageItem(INITIAL_MESSAGES_POPUP_REMOVED_KEY) == 'true'
    ) {
      return;
    }

    if (showPopupMessagesOnlyOnce) {
      setLocalStorageItem(INITIAL_MESSAGES_POPUP_REMOVED_KEY, 'true');
    }

    // Add the initial messages popup styles to the head of the document
    const styleElement = document.createElement('style');
    styleElement.textContent = getInitialMessagesPopupStyles();
    document.head.appendChild(styleElement);

    // Add the initial messages HTML to the body of the document
    const popupHTML = getInitialMessagesPopupHTML(initialMessages);
    document.body.insertAdjacentHTML('beforeend', popupHTML);

    // Function to add the active class to each message
    function activateMessages() {
      const popup = document.querySelector('.initial-messages-popup');
      const messages = document.querySelectorAll('.initial-message');
      if (popup) {
        popup.classList.add('active');
        messages.forEach((message, index) => {
          // Delay the animation for each message
          setTimeout(() => {
            message.classList.add('active');
          }, index * 500); // Delay time between messages
        });
      }
    }

    // Trigger the popup and messages to appear after the specified delay
    setTimeout(() => {
      console.log('[Chat Widget] Showing initial messages popup');
      activateMessages();
    }, delay * 1000);

    // Add event listener for the initial messages click to toggle chatwidget
    document
      .getElementById(INITIAL_MESSAGES_POPUP_ID)
      .addEventListener('click', toggleChatWidgetIframe);

    // Add event listener for the remove/close icon to permanently remove the popup
    document
      .getElementById(CLOSE_INITIAL_MESSAGES_POPUP_ID)
      .addEventListener('click', function (event) {
        event.stopPropagation(); // Prevent the click event from propagating to parent elements
        removeInitialMessagesPopup();
      });

    // setting this flag to true as it will be checked if we want to remove the popup.
    isInitialMessagesPopupShowing = true;
  }

  function showChatwidgetPopup(delay) {
    // Check if the chatwidget popup has already been show from session storage
    if (getSessionStorageItem(CHAT_WIDGET_POPUP_SHOWN_KEY) === 'true') {
      return;
    }

    if (delay >= 0) {
      setTimeout(() => {
        console.log('[Chat Widget] Auto-opening chat widget popup');
        toggleChatWidgetIframe();
        // Set the chatwidget popup as shown in session storage
        setSessionStorageItem(CHAT_WIDGET_POPUP_SHOWN_KEY, 'true');
      }, delay * 1000);
    }
  }

  function getInitialMessagesPopupStyles() {
    const styles = `
        .initial-messages-popup {
            position: fixed;
            bottom: 80px;
            ${widgetPosition === 'left' ? 'left: 20px' : 'right: 20px'};
            width: auto;
            background-color: transparent;
            display: flex;
            flex-direction: column;
            align-items: ${widgetPosition === 'left' ? 'flex-start' : 'flex-end'};
            justify-content: center;
            z-index: 2000;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.5s, visibility 0.5s;
        }
    
        .initial-message {
            color: black;
            background-color: white;
            margin-bottom: 15px;
            margin-${widgetPosition === 'left' ? 'right' : 'left'}: 15px;
            padding: 20px;
            max-width: -webkit-fill-available;
            border-radius: 10px;
            transform: translateY(20px);
            opacity: 0;
            transition: transform 0.5s, opacity 0.5s;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            border: 1px solid #ddd;
            position: relative;
            word-wrap: break-word;
        }
    
        .close-button {
            position: absolute;
            top: -15px;
            ${widgetPosition === 'left' ? 'left: -10px' : 'right: -10px'};
            font-size: 25px;
            color: #AAA;
            cursor: pointer;
            background-color: white;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            z-index: 2100;
        }
    
        .close-button:hover {
            color: #777;
        }
    
        .initial-messages-popup.active {
            opacity: 1;
            visibility: visible;
        }
        
        .initial-message.active {
            transform: translateY(0);
            opacity: 1;
        }
        `;
    return styles;
  }

  /**
   * Returns the HTML of initial messages popup
   */
  function getInitialMessagesPopupHTML(initialMessages) {
    // Ensure initialMessages is an array
    const messages = Array.isArray(initialMessages) ? initialMessages : [];

    // Create messages HTML, but add the close button only to the first message
    let messagesHTML = messages
      .map((message, index) => {
        // Only add close button to the first message (index 0)
        let closeButton =
          index === 0
            ? `<div class="close-button" id="${CLOSE_INITIAL_MESSAGES_POPUP_ID}">&times;</div>`
            : '';

        return `<div class="initial-message" style="font-size: ${initialPopupMessageFontSize}px; font-family: ${initialPopupMessageFontFamily};">
                ${closeButton}${message}
            </div>`;
      })
      .join('');

    const initialMessagesPopupHTML = `
        <div class="initial-messages-popup" id="${INITIAL_MESSAGES_POPUP_ID}">
            ${messagesHTML}
        </div>`;
    return initialMessagesPopupHTML;
  }

  /**
   * Fetches some of the chatbot's data via API and returns it.
   */
  async function getChatwidgetData(site) {
    const URL = `${domain}${GET_CHATWIDGET_DATA_API_URL}${site}/`;
    try {
      const response = await fetch(URL, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        console.error('[Chat Widget] API error:', response);
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      console.log('[Chat Widget] Widget data fetched successfully');
      return data;
    } catch (error) {
      console.error('Error fetching chat widget data:', error);
      throw new Error(
        `Something went wrong while fetching chatwidget's data. ${error}`
      );
    }
  }

  /**
   * Sets a value for a given key in the local storage.
   */
  function setLocalStorageItem(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (error) {
      console.error('Error saving to localStorage', error);
    }
  }

  /**
   * Retrieves a value from local storage by its key.
   */
  function getLocalStorageItem(key) {
    try {
      return localStorage.getItem(key);
    } catch (error) {
      console.error('Error retrieving from localStorage', error);
      return null;
    }
  }

  /**
   * Sets a value for a given key in session storage
   */
  function setSessionStorageItem(key, value) {
    try {
      sessionStorage.setItem(key, value);
    } catch (error) {
      console.log('Error saving to sessionStorage', error);
    }
  }

  /**
   * Retrieves a value from session storage by its key
   */
  function getSessionStorageItem(key) {
    try {
      return sessionStorage.getItem(key);
    } catch (error) {
      console.log('Error retrieving from sessionStorage', error);
      return null;
    }
  }
})();

