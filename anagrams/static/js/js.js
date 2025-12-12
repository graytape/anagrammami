
document.addEventListener('DOMContentLoaded', function() {
    const textbar          = document.getElementById('textbar');
    const btnSetReference  = document.getElementById('btn-set-reference');
    const btnSaveResults   = document.getElementById('btn-save-results');
    const btnSaveInDb      = document.getElementById('btn-save-in-db');
    const referenceDiv     = document.getElementById('reference');
    const savedResultsDiv  = document.getElementById('saved-results');
    const deleteButtons    = document.querySelectorAll('.delete-anagrams-btn');
    const btnGetHints      = document.getElementById('btn-get-hints');
    const hintsContainer   = document.querySelector('.hints-container');
    const hintsBox         = document.querySelector('.hints-box');
    const hintsStats       = document.querySelector('.hints-stats');
    
    let referenceText  = '';
    let availableChars = [];
    let usedIndices    = [];
    let previousValue  = '';

    window.saved_anagrams = [];
    
    // Special characters always allowed
    const specialChars = new Set(['?', '!', ',', '.', ';', ':', '-', '_', '@', '#', '(', ')', '[', ']', '{', '}', '/', '\\', '\'', '"', '+', '=', '*', '&', '%', ' ', '€', '£', '<', '>']);
     
    // Normalize - Remove accents
    function normalizeChar(char) {
      return char.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    }
    
    // Check if a character can be used
    function canUseChar(char) {
      // Spaces always allowed
      if (char === ' ') return true;
      // Special characters always allowed
      if (specialChars.has(char)) return true;
      // Find normalized character
      const normalized = normalizeChar(char);
      return availableChars.some((refChar, i) => 
        normalizeChar(refChar) === normalized && !usedIndices.includes(i)
      );
    }
    
    // Update reference view setting used chars
    function updateReferenceDisplay() {
      referenceDiv.querySelectorAll('span').forEach((span, i) => {
        if (usedIndices.includes(i)) {
          span.classList.add('used');
        } else {
          span.classList.remove('used');
        }
      });
    }


    function setReference() {
      const text = textbar.value.trim();
      if (!text) return;
      
      referenceText = text;
      availableChars = text.split('');
      usedIndices = [];
      previousValue = '';

      btnSetReference.innerHTML = btnSetReference.dataset.resettext;
      
      // reset reference
      referenceDiv.innerHTML = '';
      availableChars.forEach((char, i) => {
        const span = document.createElement('span');
        // replace space with &nbsp; for visibility
        if (char == ' ') {char = '&nbsp;'}
        span.innerHTML = char;
        span.dataset.index = i;
        referenceDiv.appendChild(span);
      });
      
      // reset textbar and enable buttons
      textbar.value = '';
      btnSaveResults.disabled = false;
      btnGetHints.disabled = false;
      if (btnSaveInDb) {
        btnSaveInDb.disabled = false;
      }
    }
       

    function handleTextBarInput(e) {
      if (!referenceText) return;
      
      const currentValue = e.target.value;
      
      // Check what changed
      let validValue = '';
      let newUsedIndices = [];
      
      // Rebuild input char by char
      for (let i = 0; i < currentValue.length; i++) {
        const char = currentValue[i];
        
        // Spaces always allowed
        if (char === ' ') {
          validValue += char;
          continue;
        }
        
        // Special characters always allowed
        if (specialChars.has(char)) {
          validValue += char;
          continue;
        }
        
        // Find normalized character
        const normalized = normalizeChar(char);
        const availableIndex = availableChars.findIndex((refChar, idx) => 
          normalizeChar(refChar) === normalized && !newUsedIndices.includes(idx)
        );
        
        if (availableIndex !== -1) {
          validValue += char;
          newUsedIndices.push(availableIndex);
        }
      }
      
      // Update values and index used
      e.target.value = validValue;
      usedIndices    = newUsedIndices;
      previousValue  = validValue;
      
      // Update view
      updateReferenceDisplay();
    }

    function saveAnagram() {
      const word = textbar.value.trim();
      if (!word) return;
      
      // Find unused chars
      const unusedChars = availableChars
        .filter((char, i) => !usedIndices.includes(i))
        .join(' ');
    
      const unusedString = unusedChars ? `<span class="result-unused"> ${unusedChars}</span>` :'';
      
      if (!saved_anagrams[referenceText]) {
        saved_anagrams[referenceText] = [];
      }
      saved_anagrams.push({'model': referenceText, 'anagram': word});

      // Create result div
      const resultItem = document.createElement('div');
      resultItem.className = 'result-item';
      resultItem.innerHTML = `
        <div class="result-word">${word}${unusedString}</div>
      `;
      
      if (btnSaveInDb) {
        btnSaveInDb.classList.remove('hidden');
      }

      // Prepend to results div
      savedResultsDiv.insertBefore(resultItem, savedResultsDiv.firstChild);
      
      // Reset textbar and index
      textbar.value = '';
      usedIndices = [];
      previousValue = '';
      
      // Update view
      updateReferenceDisplay();
    }
    

    function registerSavedAnagrams() {
        fetch('/save-anagrams/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')  // serve CSRF token
            },
            //body: JSON.stringify({ anagrams: saved_anagrams })
            body: JSON.stringify({
               model: referenceText,
               anagrams: document.getElementById('saved-results').innerText
              }
            )
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showSaveConfirm();
            } else {
                alert('Error saving anagrams: ' + data.message);
            }
        })
        .catch(error => {
            alert('Network or server error: ' + error);
        });
    }

    function deleteSavedAnagrams(id) {
      fetch('/delete-anagrams/', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify({ id: id })
      })
      .then(response => response.json())
      .then(data => {
          if (data.status === 'success') {
              const block = document.querySelector(`.myanagrams-block[data-id="${id}"]`);
              if (block) block.remove();
          } else {
              alert('Error deleting: ' + data.message);
          }
      })
      .catch(error => {
          alert('Network or server error: ' + error);
      });
    }

    function fetchHints() {
      // lang
      const lang = document.documentElement.lang || 'it';
      // Find unused chars
      const unusedChars = availableChars
        .filter((char, i) => !usedIndices.includes(i))
        .join('');
      if (!unusedChars) {
        alert(gettext("No unused characters to fetch hints for."));
        return;
      }
      // loader
      btnGetHints.innerHTML = '<span class="loader"></span>';
      fetch(`/anagrams/${lang}/fetch/${unusedChars}`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
              hintsBox.innerHTML = data.hints_html.map(hint => `<span class="hint-item">${hint}</span>`).join('');
              btnGetHints.innerHTML = btnGetHints.dataset.text;
              hintsStats.classList.add('active');
              const res_found = ngettext("%s result found for unused characters", "%s results found for unused characters", data.n_results).replace('%s', data.n_results);
              const recursions = gettext("Recursive calls: %s").replace('%s', data.recursions);
              hintsStats.innerHTML = `<span>${res_found}</span><span class="recursions">${recursions}</span>`;
            }
        })
        .catch(error => {
            alert('Network or server error: ' + error);
        });
    }



  // helper to get cookie CSRF (standard Django)
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i=0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  function showSaveConfirm(message = "Saved!") {
      const confirmBox = document.createElement('div');
      confirmBox.className = 'save-confirm';

      const text = document.createElement('span');
      text.textContent = message;

      const checkmark = document.createElement('div');
      checkmark.className = 'checkmark';

      confirmBox.appendChild(text);
      confirmBox.appendChild(checkmark);

      document.body.appendChild(confirmBox);

      setTimeout(() => {
          confirmBox.style.opacity = '0';
          // Dopo l’animazione di sparizione, rimuovi dal DOM
          setTimeout(() => confirmBox.remove(), 500);
      }, 3000);
  }


  // EVENT LISTENERS

  // Get hints
  if (btnGetHints) {
      btnGetHints.addEventListener('click', function () {
          fetchHints();
      });
  }

  // Delete saved anagrams
  if (deleteButtons) {
      deleteButtons.forEach(btn => {
          btn.addEventListener('click', function () {
              const id = this.dataset.id;
              deleteSavedAnagrams(id);
          });
      });
  }
  
  // Save reference
  if (btnSetReference) {
    btnSetReference.addEventListener('click', () => {
      if (referenceText != '') {
        btnSetReference.innerHTML = btnSetReference.dataset.settext;
        referenceText = '';
        referenceDiv.innerHTML = '';
        textbar.value = '';
        btnSaveResults.disabled = true;
        if (btnSaveInDb)  {
          btnSaveInDb.disabled = true;
        }
      } else {
          setReference();
      }
    });
  }
  
  // Handles textbar input
  if (textbar) {
    textbar.addEventListener('input', (e) => {
      handleTextBarInput(e);
    });
  }

  // Save results
  if (btnSaveResults) {
    btnSaveResults.addEventListener('click', () => {
      saveAnagram();
    });
  }

  // Save results in DB
  if (btnSaveInDb) {
    btnSaveInDb.addEventListener('click', () => {
      registerSavedAnagrams();
    });
  }

  // Handle Enter key in textbar
  if (textbar) {
    textbar.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (referenceText != '' && textbar.value.trim() !== '') {
          saveAnagram();
        } else if (referenceText === '' && textbar.value.trim() !== '') {
          setReference();
        }
      }
    });
  }

});
