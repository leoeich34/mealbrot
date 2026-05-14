import { describe, expect, it } from 'vitest';

import { buildMonthGrid, expirationStatusMeta, groupShoppingItems } from '../src/utils/ui';

describe('expirationStatusMeta', () => {
  it('maps inventory expiration statuses to Russian labels and stable color classes', () => {
    expect(expirationStatusMeta('expired')).toMatchObject({
      label: 'Просрочено',
      tone: 'danger'
    });
    expect(expirationStatusMeta('soon')).toMatchObject({
      label: 'Скоро истекает',
      tone: 'warning'
    });
    expect(expirationStatusMeta('fresh')).toMatchObject({
      label: 'В норме',
      tone: 'success'
    });
    expect(expirationStatusMeta('unknown')).toMatchObject({
      label: 'Без срока',
      tone: 'neutral'
    });
  });
});

describe('groupShoppingItems', () => {
  it('groups shopping items by category while keeping manual uncategorized items visible', () => {
    const groups = groupShoppingItems([
      { id: 1, title: 'курица', category: { name: 'мясо' } },
      { id: 2, title: 'томаты', category: { name: 'овощи' } },
      { id: 3, title: 'салфетки', category: null }
    ]);

    expect(groups.map((group) => group.name)).toEqual(['мясо', 'овощи', 'Без категории']);
    expect(groups[2].items[0].title).toBe('салфетки');
  });
});

describe('buildMonthGrid', () => {
  it('builds a Monday-first month grid and attaches entries to matching days', () => {
    const grid = buildMonthGrid(2026, 4, [
      { id: 10, planned_date: '2026-05-14', meal_slot: 'dinner' }
    ]);

    expect(grid).toHaveLength(5);
    expect(grid[0][0].date).toBe('2026-04-27');
    const target = grid.flat().find((day) => day.date === '2026-05-14');
    expect(target.isCurrentMonth).toBe(true);
    expect(target.entries).toHaveLength(1);
  });
});
