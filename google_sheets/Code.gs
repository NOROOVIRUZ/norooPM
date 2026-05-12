// noroo_Bot_asuka sourcing — Google Sheets 로그
// 배포: 확장 프로그램 → Apps Script → 배포 → 웹 앱으로 배포
// 실행 권한: 나 / 액세스: 모든 사람

const SHEET_NAME = "sourcing_log";

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sheet = ss.getSheetByName(SHEET_NAME);

    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
      sheet.appendRow(["검색일시", "카테고리", "플랫폼", "수집수", "순위", "상품명", "가격", "URL"]);
      sheet.getRange(1, 1, 1, 8).setFontWeight("bold").setBackground("#1a1a1a").setFontColor("#e63946");
    }

    const { timestamp, category, platform, top5 } = data;

    top5.forEach((product) => {
      sheet.appendRow([
        timestamp,
        category,
        platform,
        data.count,
        product.rank,
        product.name,
        product.price,
        product.url,
      ]);
    });

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet() {
  return ContentService
    .createTextOutput("noroo_Bot_asuka sourcing logger active")
    .setMimeType(ContentService.MimeType.TEXT);
}
