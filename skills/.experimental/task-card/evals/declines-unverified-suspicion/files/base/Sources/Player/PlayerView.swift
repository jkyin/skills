import UIKit

final class PlayerView: UIView {
    private let progressView = UIProgressView()

    func update(progress: Float) {
        progressView.setProgress(progress, animated: true)
    }
}
