arguments <- commandArgs(trailingOnly=TRUE)
root <- if(length(arguments)) arguments[1] else getwd()
d <- read.csv(file.path(root,'results','comparison_results.csv'),check.names=FALSE)
d <- d[d$Representation=='TF-IDF',]
models <- c('OLS','Ridge','Lasso','PLS','RF','XGB','LGBM','LinearSVR')
scores <- sapply(models,function(m) d$Adj_R2[d$Model==m & grepl('^fold',d$Split)])
means <- colMeans(scores)
plot_labels <- models
draw <- function(){
 par(mar=c(4.7,4.6,1.2,1),family='sans',las=1,cex=1.05)
 x <- barplot(means,names.arg=rep('',8),ylim=c(0,.60),col='#B9D9E8',border='#24475B',ylab=expression('Validation adjusted '*R^2),xlab='Predictor',axis.lty=1,cex.names=.8)
 mtext(plot_labels,side=1,at=x,line=2.1,cex=.8)
 abline(h=seq(0,.6,.1),col='#D7D7D7',lty=3)
 for(i in seq_len(ncol(scores))) points(rep(x[i],5)+seq(-.09,.09,length.out=5),scores[,i],pch=21,bg='#24475B',col='#24475B',cex=.95)
 text(x,apply(scores,2,max)+.026,sprintf('%.4f',means),cex=.8)
 legend('top',legend=c('Mean of five folds','Individual fold'),pch=c(22,21),pt.bg=c('#B9D9E8','#24475B'),col='#24475B',bty='n',cex=.8,horiz=TRUE,inset=.01)
}
dir.create(file.path(root,'Figures'),showWarnings=FALSE)
png(file.path(root,'Figures','Figure1.png'),width=2400,height=1500,res=300,type='cairo');draw();dev.off()
pdf(file.path(root,'Figures','Figure1.pdf'),width=8.5,height=11,useDingbats=FALSE)
par(omi=c(1,1,1,1),fig=c(0,1,.2743,.7257));draw();dev.off()
print(data.frame(Model=models,Mean=means))
