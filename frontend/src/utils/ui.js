const STATUS_META = {
  expired: {
    label: 'Просрочено',
    tone: 'danger',
    className: 'border-red-200 bg-red-50 text-red-700'
  },
  soon: {
    label: 'Скоро истекает',
    tone: 'warning',
    className: 'border-amber-200 bg-amber-50 text-amber-700'
  },
  fresh: {
    label: 'В норме',
    tone: 'success',
    className: 'border-emerald-200 bg-emerald-50 text-emerald-700'
  },
  unknown: {
    label: 'Без срока',
    tone: 'neutral',
    className: 'border-slate-200 bg-slate-50 text-slate-600'
  }
};

export function expirationStatusMeta(status) {
  return STATUS_META[status] ?? STATUS_META.unknown;
}

export function groupShoppingItems(items) {
  const groups = new Map();
  for (const item of items) {
    const name = item.category?.name ?? item.ingredient?.category?.name ?? 'Без категории';
    if (!groups.has(name)) {
      groups.set(name, { name, items: [] });
    }
    groups.get(name).items.push(item);
  }
  return [...groups.values()].sort((a, b) => {
    if (a.name === 'Без категории') return 1;
    if (b.name === 'Без категории') return -1;
    return 0;
  });
}

function toDateKey(date) {
  return date.toISOString().slice(0, 10);
}

export function buildMonthGrid(year, monthIndex, entries = []) {
  const firstOfMonth = new Date(Date.UTC(year, monthIndex, 1));
  const lastOfMonth = new Date(Date.UTC(year, monthIndex + 1, 0));
  const mondayOffset = (firstOfMonth.getUTCDay() + 6) % 7;
  const cursor = new Date(firstOfMonth);
  cursor.setUTCDate(firstOfMonth.getUTCDate() - mondayOffset);

  const entriesByDate = new Map();
  for (const entry of entries) {
    if (!entriesByDate.has(entry.planned_date)) {
      entriesByDate.set(entry.planned_date, []);
    }
    entriesByDate.get(entry.planned_date).push(entry);
  }

  const weeks = [];
  while (cursor <= lastOfMonth || cursor.getUTCDay() !== 1) {
    const week = [];
    for (let day = 0; day < 7; day += 1) {
      const date = toDateKey(cursor);
      week.push({
        date,
        day: cursor.getUTCDate(),
        isCurrentMonth: cursor.getUTCMonth() === monthIndex,
        entries: entriesByDate.get(date) ?? []
      });
      cursor.setUTCDate(cursor.getUTCDate() + 1);
    }
    weeks.push(week);
  }
  return weeks;
}

export function formatQuantity(value, unit) {
  const amount = Number.isInteger(value) ? value : Number(value).toFixed(1);
  return `${amount} ${unit}`;
}

export function mealSlotLabel(slot) {
  return {
    breakfast: 'Завтрак',
    lunch: 'Обед',
    dinner: 'Ужин'
  }[slot] ?? slot;
}
