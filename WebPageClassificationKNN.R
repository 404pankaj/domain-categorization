# Set seed for reproducible results
set.seed(12345)

# Packages
library(tm) # Text mining: Corpus and Document Term Matrix
library(class) # KNN model
library(SnowballC) # Stemming words

# Read csv with two columns: text and category
df <- read.csv("/home/pubmatic/devtools/DataScience/mydataFinal.csv", sep =",", header = TRUE)
dftest <- read.csv("/home/pubmatic/devtools/DataScience/12data.csv", sep =",", header = TRUE)
df$url.text.category

# Create corpus
docs <- Corpus(VectorSource(df$text))
doctest <- Corpus(VectorSource(dftest$text))

# Clean corpus
docs <- tm_map(docs, content_transformer(tolower))
docs <- tm_map(docs, removeNumbers)
docs <- tm_map(docs, removeWords, stopwords("english"))
docs <- tm_map(docs, removePunctuation)
docs <- tm_map(docs, stripWhitespace)
docs <- tm_map(docs, stemDocument, language = "english")

#Clean corpus for test
doctest <- tm_map(doctest, content_transformer(tolower))
doctest <- tm_map(doctest, removeNumbers)
doctest <- tm_map(doctest, removeWords, stopwords("english"))
doctest <- tm_map(doctest, removePunctuation)
doctest <- tm_map(doctest, stripWhitespace)
doctest <- tm_map(doctest, stemDocument, language = "english")

# Create dtm
dtm <- DocumentTermMatrix(docs)


dtmsmaller <- DocumentTermMatrix(docs, control=list(wordLengths=c(2,Inf),bounds = list(global = c(1,Inf))))
findFreqTerms(dtmsmaller, 1000)
dtmsmaller <-removeSparseTerms(dtmsmaller, sparse=.99)
findAssocs(dtmsmaller, "payment", 0.5)
inspect(dtmsmaller[1:500, 1:10])

######tes#######
dtmsmallertest <- DocumentTermMatrix(doctest, control=list(wordLengths=c(3,Inf),bounds = list(global = c(1,Inf))))
dtmsmallertest <-removeSparseTerms(dtmsmallertest, sparse=.99)
mattest.df <- as.data.frame(data.matrix(dtmsmallertest), stringsAsfactors = FALSE)
mattest.df  <- cbind(mmattest.df , dftest$category)
knn.pred <- knn(modeldata[train, ], mattest.df , cl[train])

########################
# Transform dtm to matrix to data frame - df is easier to work with
mat.df <- as.data.frame(data.matrix(dtmsmaller), stringsAsfactors = FALSE)

# Column bind category (known classification)
mat.df <- cbind(mat.df, df$category)

#see all columns
colnames(mat.df)
str(mat.df)

# Change name of new column to "category"
colnames(mat.df)[ncol(mat.df)] <- "category"

# Split data by rownumber into two equal portions
train <- sample(nrow(mat.df), ceiling(nrow(mat.df) * .80))
test <- (1:nrow(mat.df))[- train]

test
# Isolate classifier
cl <- mat.df[, "category"]

# Create model data and remove "category"
modeldata <- mat.df[,!colnames(mat.df) %in% "category"]

# Create model: training set, test set, training set classifier
knn.pred <- knn(modeldata[train, ], modeldata[test, ], cl[train])

# Confusion matrix
conf.mat <- table("Predictions" = knn.pred, Actual = cl[test])
conf.mat

# Accuracy
(accuracy <- sum(diag(conf.mat))/length(test) * 100)

# Create data frame with test data and predicted category
df.pred <- cbind(knn.pred, modeldata[test, ])
write.table(df.pred, file="/home/pubmatic/devtools/output85Percent.csv", sep=",")

library(wordcloud)
m <- as.matrix(dtmsmaller)
# calculate the frequency of words
v <- sort(rowSums(m), decreasing=TRUE)
myNames <- names(v)
d <- data.frame(word=myNames, freq=v)
wordcloud(d$word, d$freq, min.freq=500)

df.pred <- cbind(knn.pred, modeldata[test, ])

## Web page classification ####
thepage = readLines('http://www.google.com')
Encoding(thepage)  <- "UTF-8"
cleanFun <- function(htmlString) {
  return(gsub("<.*?>", "", htmlString))
}
thepage=cleanFun(thepage);

myCorpus = Corpus(VectorSource(thepage))
myCorpus <- tm_map(myCorpus, content_transformer(tolower))
myCorpus <- tm_map(myCorpus, removeNumbers)
myCorpus <- tm_map(myCorpus, removeWords, stopwords("english"))
myCorpus <- tm_map(myCorpus, removePunctuation)
myCorpus$text

library(RCurl)
library(RTidyHTML)
library(XML)
u <- "http://stackoverflow.com/questions/tagged?tagnames=r" 
doc.raw <- getURL(u)
doc <- tidyHTML(doc.raw)
html <- htmlTreeParse(doc, useInternal = TRUE)
txt <- xpathApply(html, "//body//text()[not(ancestor::script)][not(ancestor::style)][not(ancestor::noscript)]", xmlValue)
cat(unlist(txt))

library(RCurl)
txt <- htmlToText("https://www.google.com")

-----------------------------
  
  html <- getURL("http://stackoverflow.com/questions/3195522/is-there-a-simple-way-in-r-to-extract-only-the-text-elements-of-an-html-page")
doc = htmlParse(html, asText=TRUE)
plain.text <- xpathSApply(doc, "//text()[not(ancestor::script)][not(ancestor::style)][not(ancestor::noscript)][not(ancestor::form)]", xmlValue)
cat(paste(plain.text, collapse = " "))
df = data.frame("http://stackoverflow.com/questions/3195522/is-there-a-simple-way-in-r-to-extract-only-the-text-elements-of-an-html-page",plain.text)
write.table(df, file="/home/pubmatic/output.csv", sep=",")

# Create corpus
doc2 <- Corpus(VectorSource(plain.text))

# Clean corpus
doc2 <- tm_map(doc2, content_transformer(tolower))
doc2 <- tm_map(doc2, removeNumbers)
doc2 <- tm_map(doc2, removeWords, stopwords("english"))
doc2 <- tm_map(doc2, removePunctuation)
doc2 <- tm_map(doc2, stripWhitespace)
doc2 <- tm_map(docs, stemDocument, language = "english")
