/**
 * Hyperframes 60fps Animation & Frame Rendering Engine
 * For LeLe Chinese Factory Lesson Template
 */

(function () {
  let currentLessonData = null;

  window.setHyperframesLessonData = function (lessonData) {
    currentLessonData = lessonData;
    if (!lessonData) return;

    if (lessonData.topic) {
      const subEl = document.getElementById("topicSubtitle");
      if (subEl) subEl.innerText = `Chủ đề: ${lessonData.topic}`;
    }

    if (lessonData.pinyin) {
      const pyEl = document.getElementById("pinyinDisplay");
      if (pyEl) pyEl.innerText = lessonData.pinyin;
    }

    if (lessonData.chinese_text) {
      const hzEl = document.getElementById("hanziDisplay");
      if (hzEl) {
        hzEl.innerHTML = "";
        const chars = Array.from(lessonData.chinese_text);
        chars.forEach((c, idx) => {
          const span = document.createElement("span");
          span.className = "hanzi-char";
          span.id = `hz-char-${idx}`;
          span.innerText = c;
          hzEl.appendChild(span);
        });
      }
    }

    if (lessonData.han_viet) {
      const hvEl = document.getElementById("hanVietDisplay");
      if (hvEl) hvEl.innerText = `Hán Việt: ${lessonData.han_viet}`;
    }

    if (lessonData.vietnamese_translation) {
      const meanEl = document.getElementById("meaningDisplay");
      if (meanEl) meanEl.innerText = lessonData.vietnamese_translation;
    }
  };

  window.hyperframesRenderFrame = function (frameNumber, totalFrames, fps = 60) {
    const currentMs = (frameNumber / fps) * 1000;
    if (!currentLessonData || !currentLessonData.cues) return;

    const cues = currentLessonData.cues;
    cues.forEach((cue, idx) => {
      const span = document.getElementById(`hz-char-${idx}`);
      if (span) {
        if (currentMs >= cue.start_ms && currentMs <= cue.end_ms) {
          span.classList.add("active");
        } else {
          span.classList.remove("active");
        }
      }
    });
  };

  console.log("Hyperframes 60fps Engine loaded.");
})();
