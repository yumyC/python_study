import * as XLSX from 'xlsx'

// 导出数据到 Excel
export function exportToExcel(data: any[], filename: string, sheetName = 'Sheet1') {
  // 创建工作簿
  const wb = XLSX.utils.book_new()
  
  // 创建工作表
  const ws = XLSX.utils.json_to_sheet(data)
  
  // 添加工作表到工作簿
  XLSX.utils.book_append_sheet(wb, ws, sheetName)
  
  // 导出文件
  XLSX.writeFile(wb, `${filename}.xlsx`)
}

// 格式化日期
export function formatDate(date: string | Date, format = 'YYYY-MM-DD'): string {
  const d = new Date(date)
  
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year.toString())
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

// 下载文件
export function downloadFile(url: string, filename: string) {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}