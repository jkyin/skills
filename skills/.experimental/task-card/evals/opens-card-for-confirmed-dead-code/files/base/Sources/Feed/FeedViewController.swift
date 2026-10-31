import UIKit

final class FeedViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        if false {
            legacyBadgeSync()
        }
    }

    // legacyBadgeSync 由旧版角标逻辑使用，新版改为 BadgeCenter 推送
    private func legacyBadgeSync() {
        NotificationCenter.default.post(name: .init("LegacyBadgeSync"), object: nil)
    }
}
