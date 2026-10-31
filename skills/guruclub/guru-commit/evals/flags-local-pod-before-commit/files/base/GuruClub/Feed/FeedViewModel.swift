import GuruKit

final class FeedViewModel {
    func reload() {
        FeedService.shared.fetch()
    }
}
