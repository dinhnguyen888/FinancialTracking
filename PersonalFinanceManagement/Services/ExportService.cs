using System;
using System.IO;
using System.Threading.Tasks;
using System.Linq;
using System.Collections.Generic;
using Microsoft.Win32;
using ClosedXML.Excel;
using PersonalFinanceManagement.Models;

namespace PersonalFinanceManagement.Services
{
    public interface IExportService
    {
        Task ExportToExcelAsync(
            IEnumerable<Income> incomes,
            IEnumerable<Expense> expenses,
            DateTime startDate,
            DateTime endDate);
    }

    public class ExportService : IExportService
    {
        public async Task ExportToExcelAsync(
            IEnumerable<Income> incomes,
            IEnumerable<Expense> expenses,
            DateTime startDate,
            DateTime endDate)
        {
            var dialog = new SaveFileDialog
            {
                Filter = "Excel Files|*.xlsx",
                DefaultExt = ".xlsx",
                FileName = $"Báo_Cáo_Tài_Chính_{startDate:dd-MM-yyyy}_đến_{endDate:dd-MM-yyyy}"
            };

            if (dialog.ShowDialog() == true)
            {
                await Task.Run(() =>
                {
                    using var workbook = new XLWorkbook();
                    
                    // Create Income Sheet
                    var incomeSheet = workbook.Worksheets.Add("Thu nhập");
                    AddIncomeData(incomeSheet, incomes);

                    // Create Expense Sheet
                    var expenseSheet = workbook.Worksheets.Add("Chi tiêu");
                    AddExpenseData(expenseSheet, expenses);

                    // Create Summary Sheet
                    var summarySheet = workbook.Worksheets.Add("Tổng kết");
                    AddSummaryData(summarySheet, incomes, expenses);

                    workbook.SaveAs(dialog.FileName);
                });
            }
        }

        private void AddIncomeData(IXLWorksheet sheet, IEnumerable<Income> incomes)
        {
            // Headers
            sheet.Cell(1, 1).Value = "Ngày";
            sheet.Cell(1, 2).Value = "Số tiền (VNĐ)";
            sheet.Cell(1, 3).Value = "Danh mục";
            sheet.Cell(1, 4).Value = "Nguồn thu";
            sheet.Cell(1, 5).Value = "Ghi chú";

            // Style headers
            var headerRow = sheet.Row(1);
            headerRow.Style.Font.Bold = true;
            headerRow.Style.Fill.BackgroundColor = XLColor.LightGray;

            // Data
            int row = 2;
            foreach (var income in incomes.OrderBy(i => i.Date))
            {
                sheet.Cell(row, 1).Value = income.Date;
                sheet.Cell(row, 2).Value = income.Amount;
                sheet.Cell(row, 3).Value = income.Category?.Name;
                sheet.Cell(row, 4).Value = income.Source;
                sheet.Cell(row, 5).Value = income.Description;
                row++;
            }

            // Format
            sheet.Column(1).Style.DateFormat.Format = "dd/MM/yyyy";
            sheet.Column(2).Style.NumberFormat.Format = "#,##0";
            sheet.Columns().AdjustToContents();
        }

        private void AddExpenseData(IXLWorksheet sheet, IEnumerable<Expense> expenses)
        {
            // Headers
            sheet.Cell(1, 1).Value = "Ngày";
            sheet.Cell(1, 2).Value = "Số tiền (VNĐ)";
            sheet.Cell(1, 3).Value = "Danh mục";
            sheet.Cell(1, 4).Value = "Phương thức";
            sheet.Cell(1, 5).Value = "Thiết yếu";
            sheet.Cell(1, 6).Value = "Ghi chú";

            // Style headers
            var headerRow = sheet.Row(1);
            headerRow.Style.Font.Bold = true;
            headerRow.Style.Fill.BackgroundColor = XLColor.LightGray;

            // Data
            int row = 2;
            foreach (var expense in expenses.OrderBy(e => e.Date))
            {
                sheet.Cell(row, 1).Value = expense.Date;
                sheet.Cell(row, 2).Value = expense.Amount;
                sheet.Cell(row, 3).Value = expense.Category?.Name;
                sheet.Cell(row, 4).Value = expense.PaymentMethod;
                sheet.Cell(row, 5).Value = expense.IsEssential ? "Có" : "Không";
                sheet.Cell(row, 6).Value = expense.Description;
                row++;
            }

            // Format
            sheet.Column(1).Style.DateFormat.Format = "dd/MM/yyyy";
            sheet.Column(2).Style.NumberFormat.Format = "#,##0";
            sheet.Columns().AdjustToContents();
        }

        private void AddSummaryData(IXLWorksheet sheet, IEnumerable<Income> incomes, IEnumerable<Expense> expenses)
        {
            // Title
            sheet.Cell(1, 1).Value = "Báo Cáo Tổng Kết";
            sheet.Range(1, 1, 1, 2).Merge().Style.Font.Bold = true;

            // Income Summary
            sheet.Cell(3, 1).Value = "Tổng thu nhập:";
            sheet.Cell(3, 2).Value = incomes.Sum(i => i.Amount);

            // Expense Summary
            sheet.Cell(4, 1).Value = "Tổng chi tiêu:";
            sheet.Cell(4, 2).Value = expenses.Sum(e => e.Amount);

            // Balance
            sheet.Cell(5, 1).Value = "Số dư:";
            sheet.Cell(5, 2).Value = incomes.Sum(i => i.Amount) - expenses.Sum(e => e.Amount);

            // Essential vs Non-Essential Expenses
            sheet.Cell(7, 1).Value = "Chi tiêu thiết yếu:";
            sheet.Cell(7, 2).Value = expenses.Where(e => e.IsEssential).Sum(e => e.Amount);

            sheet.Cell(8, 1).Value = "Chi tiêu không thiết yếu:";
            sheet.Cell(8, 2).Value = expenses.Where(e => !e.IsEssential).Sum(e => e.Amount);

            // Format
            sheet.Column(2).Style.NumberFormat.Format = "#,##0";
            sheet.Columns().AdjustToContents();

            // Style
            var range = sheet.Range(3, 1, 8, 2);
            range.Style.Border.OutsideBorder = XLBorderStyleValues.Thin;
            range.Style.Border.InsideBorder = XLBorderStyleValues.Thin;
        }
    }
}