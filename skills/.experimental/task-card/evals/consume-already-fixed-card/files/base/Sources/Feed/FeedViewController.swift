import UIKit

final class FeedViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        BadgeCenter.shared.subscribe(self)
    }
}
