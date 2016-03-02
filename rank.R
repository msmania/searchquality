GetScore <- function(sd1, sd2, pagesize, rank) {
    GetPageScore <- function(sd, x) {
        return ((pnorm(x, sd = sd) - pnorm(x - 1, sd = sd)) * 2)
    }
    GetInPageRankScore <- function(sd, pagesize, x) {
        return ((pnorm(x, sd = sd) - pnorm(x - 1, sd = sd))
            / (pnorm(pagesize, sd = sd) - .5))
    }
    page <- (rank - 1) %/% pagesize + 1
    pos <- (rank - 1) %% pagesize + 1
    score_page <- GetPageScore(sd = sd1, x = page)
    score_pos <- GetInPageRankScore(sd = sd2, pagesize = 10, x = pos)
    # print(sprintf('%.6f %.6f', score_page, score_pos))
    return (score_page * score_pos)
}
nresults <- 100
x <- 1:nresults
plotdata <- data.frame(rank=x, score=GetScore(.5, 10, pagesize=10, rank=x))
plot(plotdata$rank, plotdata$score)
