// API 호출 및 결과 렌더링 스크립트

/**
 * API를 호출하여 DDD 계산 결과를 가져옵니다.
 */
async function calculateDDD(formData) {
  const response = await fetch('/api/v1/calculate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(formData),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'API request failed');
  }

  return await response.json();
}

/**
 * 폼 제출을 처리하고 API를 호출합니다.
 */
function setupFormSubmit() {
  const form = document.getElementById('calcForm');
  const errBox = document.getElementById('clientErrors');
  const errList = document.getElementById('clientErrorList');
  const resultSection = document.getElementById('resultSection');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // 에러 초기화
    errList.innerHTML = '';
    errBox.style.display = 'none';

    // 폼 데이터 수집
    const yyyy = document.getElementById('yyyy').value;
    const mm = document.getElementById('mm').value;
    const dd = document.getElementById('dd').value;
    const termKind = document.getElementById('term_kind').value;
    const days = document.getElementById('days').value;

    // 유효성 검사
    if (yyyy.length !== 4 || !mm || !dd || !isValidIsoDate(yyyy, mm, dd)) {
      const li = document.createElement('li');
      li.textContent = window.translations?.valid_date_required || 'Please enter a valid date.';
      errList.appendChild(li);
      errBox.style.display = 'block';
      return;
    }

    const deliveryDate = `${yyyy}-${pad2(mm)}-${pad2(dd)}`;

    // 선택된 국가 코드 수집
    const countryCodes = Array.from(selectedCountries);

    if (countryCodes.length === 0) {
      const li = document.createElement('li');
      li.textContent = window.translations?.country_required || 'Please select at least one country.';
      errList.appendChild(li);
      errBox.style.display = 'block';
      return;
    }

    // DDD의 경우 days 필수
    let termDays = null;
    if (termKind === 'DDD') {
      termDays = parseInt(days);
      if (!days || isNaN(termDays)) {
        const li = document.createElement('li');
        li.textContent = window.translations?.days_required || 'Days is required for DDD term.';
        errList.appendChild(li);
        errBox.style.display = 'block';
        return;
      }
    }

    // 체크박스 값 읽기
    const includeWeekends = document.getElementById('includeWeekends').checked;
    const includeDeliveryAsDayOne = document.getElementById('includeDeliveryAsDayOne').checked;

    // API 요청 데이터 구성
    const requestData = {
      delivery_date: deliveryDate,
      country_codes: countryCodes,
      term_kind: termKind,
      days: termDays,
      skip_weekends: !includeWeekends,  // 체크하면 주말 포함 (skip_weekends=false)
      skip_holidays: true,
      include_delivery_as_day_one: includeDeliveryAsDayOne,
    };

    try {
      // 로딩 상태 표시 (선택 사항)
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalBtnText = submitBtn.textContent;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Calculating...';

      // API 호출
      const result = await calculateDDD(requestData);

      // 결과 렌더링
      renderResult(result);

      // 버튼 상태 복원
      submitBtn.disabled = false;
      submitBtn.textContent = originalBtnText;

    } catch (error) {
      console.error('API Error:', error);
      const li = document.createElement('li');
      li.textContent = error.message || 'An error occurred while calculating.';
      errList.appendChild(li);
      errBox.style.display = 'block';

      // 버튼 상태 복원
      const submitBtn = form.querySelector('button[type="submit"]');
      submitBtn.disabled = false;
      submitBtn.textContent = window.translations?.calculate_button || 'Calculate';
    }
  });
}

/**
 * API 응답 결과를 화면에 렌더링합니다.
 */
function renderResult(result) {
  const resultSection = document.getElementById('resultSection');

  if (!resultSection) {
    console.error('Result section not found');
    return;
  }

  const t = window.translations || {};

  // 결과 HTML 생성
  const html = `
    <div class="card">
      <h2 style="margin-top: 0; font-size: 1.8rem; color: var(--primary);">
        ${t.result_title || 'Due Date'}: ${result.due_date}
      </h2>

      <div style="margin-top: 16px; padding: 12px; background: rgba(37, 99, 235, 0.05); border-radius: 12px; border-left: 4px solid var(--primary);">
        <p style="margin: 4px 0;"><strong>${t.delivery || 'Delivery'}:</strong> ${result.delivery_date} + ${result.days || 0} DDD</p>
        <p style="margin: 4px 0;"><strong>${t.countries || 'Countries'}:</strong> ${result.country_codes.join(', ')}</p>
      </div>

      <div style="margin-top: 16px;">
        ${(result.excluded_weekends.length > 0 || result.excluded_holidays.length > 0) ? `
          <h3 style="font-size: 1.1rem; margin-bottom: 8px;">${t.excluded_days || 'Excluded Days'}</h3>
        ` : ''}

        <!-- Calendar Visualization -->
        <div id="calendarView" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-bottom: 16px;"></div>

        ${result.excluded_weekends.length > 0 ? `
          <details style="margin-bottom: 8px;">
            <summary style="cursor: pointer; font-weight: 600; color: var(--muted); padding: 8px; background: rgba(148, 163, 184, 0.1); border-radius: 8px;">
              ${t.weekends || 'Weekends'} (${result.excluded_weekends.length})
            </summary>
            <div style="margin-top: 8px; padding: 8px; max-height: 150px; overflow-y: auto;">
              ${result.excluded_weekends.map(date => `<span class="date-badge">${date}</span>`).join('')}
            </div>
          </details>
        ` : ''}

        ${result.excluded_holidays.length > 0 ? `
          <details style="margin-bottom: 8px;">
            <summary style="cursor: pointer; font-weight: 600; color: var(--success); padding: 8px; background: rgba(18, 128, 90, 0.08); border-radius: 8px;">
              ${t.holidays || 'Holidays'} (${result.excluded_holidays.length})
            </summary>
            <div style="margin-top: 8px; padding: 8px; max-height: 150px; overflow-y: auto;">
              ${result.excluded_holidays.map(date => `<span class="date-badge holiday">${date}</span>`).join('')}
            </div>
          </details>
        ` : ''}
      </div>
    </div>
  `;

  resultSection.innerHTML = html;
  resultSection.style.display = 'block';

  // 캘린더 렌더링 (항상 표시)
  renderCalendar(
    result.delivery_date,
    result.due_date,
    result.excluded_weekends,
    result.excluded_holidays,
    result.holiday_names || {}
  );
}

// 페이지 로드 시 폼 제출 핸들러 등록
document.addEventListener('DOMContentLoaded', () => {
  setupFormSubmit();
});
