import 'package:flutter/material.dart';
import '../data/storage.dart';
import '../data/firestore_service.dart';
import '../models/models.dart';
import '../widgets/purchase_dialog.dart';

class PurchasesScreen extends StatefulWidget {
  const PurchasesScreen({super.key});
  @override
  State<PurchasesScreen> createState() => _PurchasesScreenState();
}

class _PurchasesScreenState extends State<PurchasesScreen> {
  List<Purchase> _purchases = [];
  String _tab = 'all';

  @override
  void initState() {
    super.initState();
    _load();
    FirestoreService.dataChanges.listen((_) {
      _load();
    });
  }

  Future<void> _load() async {
    final p = await Storage.loadPurchases();
    setState(() => _purchases = p);
  }

  List<Purchase> get _filtered {
    var list = _purchases;
    if (_tab == 'large') list = list.where((p) => p.type == 'large').toList();
    else if (_tab == 'regular') list = list.where((p) => p.type == 'regular').toList();
    return list;
  }

  Map<String, List<Purchase>> get _grouped {
    final map = <String, List<Purchase>>{};
    for (final p in _filtered) {
      final key = p.date.isEmpty ? 'Без даты' : p.date;
      map.putIfAbsent(key, () => []);
      map[key]!.add(p);
    }
    final sorted = map.entries.toList()..sort((a, b) {
      if (a.key == 'Без даты') return 1;
      if (b.key == 'Без даты') return -1;
      return b.key.compareTo(a.key);
    });
    return {for (final e in sorted) e.key: e.value};
  }

  Future<void> _toggle(String id) async {
    final idx = _purchases.indexWhere((p) => p.id == id);
    if (idx == -1) return;
    _purchases[idx].done = !_purchases[idx].done;
    await Storage.savePurchases(_purchases);
    setState(() {});
  }

  Future<void> _delete(String id) async {
    _purchases.removeWhere((p) => p.id == id);
    await Storage.savePurchases(_purchases);
    setState(() {});
  }

  Future<void> _showDialog(Purchase? purchase) async {
    final result = await showDialog<Purchase>(
      context: context,
      builder: (_) => PurchaseDialog(purchase: purchase),
    );
    if (result == null) return;
    if (purchase == null) {
      _purchases.insert(0, result);
    } else {
      final idx = _purchases.indexWhere((p) => p.id == result.id);
      if (idx != -1) _purchases[idx] = result;
    }
    await Storage.savePurchases(_purchases);
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final grouped = _grouped;
    final total = _purchases.length;
    final large = _purchases.where((p) => p.type == 'large').length;
    final regular = _purchases.where((p) => p.type == 'regular').length;

    return Scaffold(
      appBar: AppBar(
        title: const Text('🛒 Покупки'),
        actions: [
          IconButton(icon: const Icon(Icons.add), onPressed: () => _showDialog(null)),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            child: Text('Всего: $total · Крупных: $large · Повседневных: $regular',
              style: const TextStyle(fontSize: 13, color: Colors.grey)),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: 'all', label: Text('Все')),
                ButtonSegment(value: 'large', label: Text('Крупные')),
                ButtonSegment(value: 'regular', label: Text('Повседневные')),
              ],
              selected: {_tab},
              onSelectionChanged: (s) => setState(() => _tab = s.first),
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: grouped.isEmpty
                ? const Center(child: Text('Нет покупок', style: TextStyle(color: Colors.grey)))
                : ListView(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    children: grouped.entries.map((entry) {
                      final dateKey = entry.key;
                      final items = entry.value;
                      final dayTotal = items.fold<double>(0, (s, p) => s + p.amount);
                      items.sort((a, b) => a.done == b.done ? 0 : a.done ? 1 : -1);

                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Padding(
                            padding: const EdgeInsets.only(top: 8, bottom: 4),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text('📅 ${dateKey == 'Без даты' ? 'Без даты' : dateKey}',
                                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: Color(0xFF2D5A3E))),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: Colors.grey.shade200,
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text('${dayTotal.toStringAsFixed(0)} ₽',
                                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
                                ),
                              ],
                            ),
                          ),
                          ...items.map((p) => _buildItem(p)),
                        ],
                      );
                    }).toList(),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildItem(Purchase p) {
    final catColors = {
      'Продукты': const Color(0xFF7BC47F),
      'Хозяйственные': const Color(0xFF7BC47F),
      'Ремонт': const Color(0xFFF7C948),
      'Одежда': const Color(0xFFC4A8D5),
      'Техника': const Color(0xFFA9D3F2),
      'Другое': const Color(0xFFCDD6D8),
    };
    final color = catColors[p.category] ?? Colors.grey;
    final typeTag = p.type == 'large' ? 'Крупная' : 'Повседневная';

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 2),
      child: ListTile(
        contentPadding: const EdgeInsets.only(left: 4, right: 0),
        leading: Checkbox(value: p.done, onChanged: (_) => _toggle(p.id)),
        title: Row(
          children: [
            Container(width: 12, height: 12, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
            const SizedBox(width: 8),
            Flexible(
              child: Text(p.title, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15), overflow: TextOverflow.ellipsis),
            ),
            const SizedBox(width: 4),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
              decoration: BoxDecoration(
                color: p.type == 'large' ? const Color(0xFFF7C948).withOpacity(0.2) : const Color(0xFFA8D5BA).withOpacity(0.3),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(typeTag, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600,
                color: p.type == 'large' ? const Color(0xFF7A6300) : const Color(0xFF2D6A3E))),
            ),
          ],
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('💰 ${p.amount.toStringAsFixed(0)} ₽', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
            if (p.comment.isNotEmpty)
              Text(p.comment, style: const TextStyle(fontSize: 12, color: Colors.grey), maxLines: 1, overflow: TextOverflow.ellipsis),
          ],
        ),
        trailing: SizedBox(
          width: 72,
          child: Row(
            children: [
              IconButton(icon: const Icon(Icons.edit_outlined, size: 18), onPressed: () => _showDialog(p)),
              IconButton(icon: const Icon(Icons.delete_outline, size: 18, color: Colors.red), onPressed: () => _delete(p.id)),
            ],
          ),
        ),
      ),
    );
  }
}
