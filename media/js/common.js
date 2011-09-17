function formatDate(dateStr)
{
    date = new Date(dateStr);
    return date.format("dd/mm/yyyy HH:MM:ss");
}