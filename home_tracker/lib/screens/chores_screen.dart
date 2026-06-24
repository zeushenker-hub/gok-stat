import 'package:flutter/material.dart';
import '../data/storage.dart';
import '../models/models.dart';
import '../widgets/chore_dialog.dart';

class ChoresScreen extends StatefulWidget {
  const ChoresScreen({super.key});
  @override
  State<ChoresScreen> createState() => _ChoresScreenState();
}

class _ChoresScreenState extends State<ChoresScreen> {
  List<Chore> _chores = [];
  List<String> _categories = [];
  String _filterCategory = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final c = await Storage.loadChores();
    final cats = await Storage.loadCategories();
    setState(() {
      _chores = c;
      _categories = cats;
    });
  }

  List<Chore> get _filtered {
    var list = _chores;
    if (_filterCategory.isNotEmpty) {
      list = list.where((c) => c.category == _filterCategory).toList();
    }
    list.sort((a, b) {
      if (a.done != b.done) return a.done ? 1 : -1;
      return 0;
    });
    return list;
  }

  Future<void> _toggle(String id) async {
    final idx = _chores.indexWhere((c) => c.id == id);
    if (idx == -1) return;
    _chores[idx].done = !_chores[idx].done;
    await Storage.saveChores(_chores);
    setState(() {});
  }

  Future<void> _delete(String id) async {
    _chores.removeWhere((c) => c.id == id);
    await Storage.saveChores(_chores);
    setState(() {});
  }

  Future<void> _save(Chore? chore) async {
    if (chore != null) {
      final idx = _chores.indexWhere((c) => c.id == chore.id);
      if (idx != -1) {
        _chores[idx] = chore;
      }
    }
    await Storage.saveChores(_chores);
    setState(() {});
  }

  Future<void> _showDialog(Chore? chore) async {
    final result = await showDialog<Chore>(
      context: context,
      builder: (_) => ChoreDialog(
        chore: chore,
        categories: _categories,
        onManageCategories: _manageCategories,
      ),
    );
    if (result == null) return;
    if (chore == null) {
      _chores.insert(0, result);
    } else {
      final idx = _chores.indexWhere((c) => c.id == result.id);
      if (idx != -1) _chores[idx] = result;
    }
    await _save(null);
  }

  Future<void> _manageCategories() async {
    final result = await showDialog<List<String>>(
      context: context,
      builder: (_) => _CategoryDialog(categories: List.from(_categories)),
    );
    if (result != null) {
      _categories = result;
      await Storage.saveCategories(_categories);
      if (!_categories.contains(_filterCategory)) _filterCategory = '';
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final filtered = _filtered;
    return Scaffold(
      appBar: AppBar(
        title: const Text('🧹 Дела по дому'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _showDialog(null),
          ),
        ],
      ),
      body: Column(
        children: [
          _CategoryFilterChips(
            categories: _categories,
            selected: _filterCategory,
            onSelected: (c) => setState(() => _filterCategory = c),
            onManage: _manageCategories,
          ),
          Expanded(
            child: filtered.isEmpty
                ? const Center(child: Text('Нет дел', style: TextStyle(color: Colors.grey)))
                : ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    itemCount: filtered.length,
                    itemBuilder: (_, i) {
                      final c = filtered[i];
                      final prioColor = c.priority == 'Высокий'
                          ? Colors.red
                          : c.priority == 'Низкий'
                              ? Colors.green
                              : Colors.orange;
                      return Card(
                        margin: const EdgeInsets.symmetric(vertical: 3),
                        child: ListTile(
                          leading: Checkbox(
                            value: c.done,
                            onChanged: (_) => _toggle(c.id),
                          ),
                          title: Text(
                            c.title,
                            style: TextStyle(
                              fontWeight: FontWeight.w600,
                              fontSize: 15,
                              decoration: c.done ? TextDecoration.lineThrough : null,
                            ),
                          ),
                          subtitle: Text(
                            '${c.category}${c.assignee.isNotEmpty ? ' · 👤 ${c.assignee}' : ''}${c.date.isNotEmpty ? ' · 📅 ${c.date}' : ''}',
                            style: const TextStyle(fontSize: 13),
                          ),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text('🔴🟡🟢'['ВысокийНизкийСредний'.indexOf(c.priority) >= 0 ? 0 : 0].toString(), style: TextStyle(fontSize: 20, color: prioColor)),
                              IconButton(
                                icon: const Icon(Icons.edit_outlined, size: 18),
                                onPressed: () => _showDialog(c),
                              ),
                              IconButton(
                                icon: const Icon(Icons.delete_outline, size: 18, color: Colors.red),
                                onPressed: () => _delete(c.id),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

class _CategoryFilterChips extends StatelessWidget {
  final List<String> categories;
  final String selected;
  final ValueChanged<String> onSelected;
  final VoidCallback onManage;

  const _CategoryFilterChips({
    required this.categories, required this.selected,
    required this.onSelected, required this.onManage,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            _chip('Все', '', selected, onSelected, context),
            ...categories.map((c) => _chip(c, c, selected, onSelected, context)),
            IconButton(
              icon: const Icon(Icons.settings, size: 18),
              onPressed: onManage,
              tooltip: 'Управление категориями',
            ),
          ],
        ),
      ),
    );
  }

  Widget _chip(String label, String value, String sel, ValueChanged<String> onSel, BuildContext context) {
    final active = sel == value;
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: FilterChip(
        label: Text(label, style: TextStyle(fontSize: 12, color: active ? Colors.white : null)),
        selected: active,
        onSelected: (_) => onSel(value),
        selectedColor: Theme.of(context).colorScheme.primary,
        checkmarkColor: Colors.white,
        visualDensity: VisualDensity.compact,
      ),
    );
  }
}

class _CategoryDialog extends StatefulWidget {
  final List<String> categories;
  const _CategoryDialog({required this.categories});
  @override
  State<_CategoryDialog> createState() => _CategoryDialogState();
}

class _CategoryDialogState extends State<_CategoryDialog> {
  late List<String> _cats;
  final _controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    _cats = List.from(widget.categories);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _add() {
    final name = _controller.text.trim();
    if (name.isEmpty) return;
    setState(() {
      _cats.add(name);
      _controller.clear();
    });
  }

  void _remove(int i) {
    if (i == 0) return;
    setState(() => _cats.removeAt(i));
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Категории'),
      content: SizedBox(
        width: 300,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                      hintText: 'Новая категория',
                      border: OutlineInputBorder(),
                      isDense: true,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(onPressed: _add, icon: const Icon(Icons.add)),
              ],
            ),
            const SizedBox(height: 12),
            Flexible(
              child: ListView(
                shrinkWrap: true,
                children: List.generate(_cats.length, (i) {
                  return ListTile(
                    dense: true,
                    title: Text(_cats[i]),
                    trailing: i == 0 ? null : IconButton(
                      icon: const Icon(Icons.delete_outline, color: Colors.red, size: 18),
                      onPressed: () => _remove(i),
                    ),
                  );
                }),
              ),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Отмена'),
        ),
        FilledButton(
          onPressed: () => Navigator.pop(context, _cats),
          child: const Text('Готово'),
        ),
      ],
    );
  }
}
