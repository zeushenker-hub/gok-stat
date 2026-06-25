class Purchase {
  final String id;
  final String title;
  final String type;
  final String category;
  final String date;
  final double amount;
  final String comment;
  String purchaseStatus; // 'planned' or 'purchased'

  Purchase({
    required this.id,
    required this.title,
    this.type = 'regular',
    this.category = 'Продукты',
    required this.date,
    this.amount = 0,
    this.comment = '',
    this.purchaseStatus = 'planned',
  });

  Map<String, dynamic> toJson() => {
    'id': id, 'title': title, 'type': type, 'category': category,
    'date': date, 'amount': amount, 'comment': comment, 'purchaseStatus': purchaseStatus,
  };

  factory Purchase.fromJson(Map<String, dynamic> j) => Purchase(
    id: j['id'] as String,
    title: j['title'] as String,
    type: j['type'] as String? ?? 'regular',
    category: j['category'] as String? ?? 'Продукты',
    date: j['date'] as String,
    amount: (j['amount'] as num?)?.toDouble() ?? 0,
    comment: j['comment'] as String? ?? '',
    purchaseStatus: j['purchaseStatus'] as String? ?? (j['done'] == true ? 'purchased' : 'planned'),
  );
}
