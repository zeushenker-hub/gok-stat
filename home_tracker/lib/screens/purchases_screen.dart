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
  String _tab = 'all'; // all, planned, purchased

  @override
  void initState() {
    super.initState();
    _load();
    FirestoreService.dataChanges.listen((_) => _load());
  }

  Future<void> _load() async {
    final p = await Storage.loadPurchases();
    setState(() => _purchases = p);
  }

  List<Purchase> get _filtered {
    var list = _purchases;
    if (_tab == 'planned') list = list.where((p) => p.purchaseStatus == 'planned').toList();
    if (_tab == 'purchased') list = list.where((p) => p.purchaseStatus == 'purchased').toList();
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

  Future<void> _toggleStatus(String id) async {
    final idx = _purchases.indexWhere((p) => p.id == id);
    if (idx == -1) return;
    _purchases[idx].purchaseStatus =
        _purchases[idx].purchaseStatus == 'planned' ? 'purchased' : 'planned';
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

    // Statistics
    final totalPlanned = _purchases.where((p) => p.purchaseStatus == 'planned').fold<double>(0, (s, p) => s + p.amount);
    final totalPurchased = _purchases.where((p) => p.purchaseStatus == 'purchased').fold<double>(0, (s, p) => s + p.amount);
    final plannedCount = _purchases.where((p) => p.purchaseStatus == 'planned').length;
    final purchasedCount = _purchases.where((p) => p.purchaseStatus == 'purchased').length;

    return Scaffold(
      appBar: AppBar(
        title: const Text('🛒 Покупки'),
        actions: [
          IconButton(icon: const Icon(Icons.add), onPressed: () => _showDialog(null)),
        ],
      ),
      body: Column(
        children: [
          // Summary card
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 8, 12, 4),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('📋 Запланировано', style: TextStyle(fontSize: 12, color: Colors.grey)),
                          Text('${totalPlanned.toStringAsFixed(0)} ₽', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Colors.orange)),
                          Text('$plannedCount шт.', style: const TextStyle(fontSize: 11, color: Colors.grey)),
                        ],
                      ),
                    ),
                    Container(width: 1, height: 40, color: Colors.grey.shade300),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          const Text('✅ Куплено', style: TextStyle(fontSize: 12, color: Colors.grey)),
                          Text('${totalPurchased.toStringAsFixed(0)} ₽', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Colors.green)),
                          Text('$purchasedCount шт.', style: const TextStyle(fontSize: 11, color: Colors.grey)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          // Filter tabs
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: 'all', label: Text('Все')),
                ButtonSegment(value: 'planned', label: Text('📋 План')),
                ButtonSegment(value: 'purchased', label: Text('✅ Куплено')),
              ],
              selected: {_tab},
              onSelectionChanged: (s) => setState(() => _tab = s.first),
            ),
          ),
          const SizedBox(height: 4),
          // Grouped list
          Expanded(
            child: grouped.isEmpty
                ? const Center(child: Text('Нет покупок', style: TextStyle(color: Colors.grey)))
                : ListView(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    children: grouped.entries.map((entry) {
                      final dateKey = entry.key;
                      final items = entry.value;
                      final dayTotal = items.fold<double>(0, (s, p) => s + p.amount);
                      items.sort((a, b) => a.purchaseStatus == b.purchaseStatus ? 0 : a.purchaseStatus == 'purchased' ? 1 : -1);

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
    final isPurchased = p.purchaseStatus == 'purchased';
    final typeTag = p.type == 'large' ? 'Крупная' : 'Повседневная';

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 2),
      child: ListTile(
        contentPadding: const EdgeInsets.only(left: 4, right: 0),
        leading: Checkbox(
          value: isPurchased,
          onChanged: (_) => _toggleStatus(p.id),
          activeColor: Colors.green,
        ),
        title: Row(
          children: [
            Container(width: 12, height: 12, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
            const SizedBox(width: 8),
            Flexible(
              child: Text(
                p.title,
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 15,
                  decoration: isPurchased ? TextDecoration.lineThrough : null,
                  color: isPurchased ? Colors.grey : null,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
            const SizedBox(width: 4),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
              decoration: BoxDecoration(
                color: isPurchased
                    ? const Color(0xFFA8D5BA).withOpacity(0.3)
                    : const Color(0xFFF7C948).withOpacity(0.2),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                isPurchased ? 'Куплено' : 'План',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: isPurchased ? const Color(0xFF2D6A3E) : const Color(0xFF7A6300),
                ),
              ),
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
          width: 80,
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              IconButton(
                icon: const Icon(Icons.edit_outlined, size: 18),
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(minWidth: 36, minHeight: 36),
                onPressed: () => _showDialog(p),
              ),
              IconButton(
                icon: const Icon(Icons.delete_outline, size: 18, color: Colors.red),
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(minWidth: 36, minHeight: 36),
                onPressed: () => _delete(p.id),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
