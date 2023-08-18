<template>
    <Layout>
        <Content :style="{padding: '0 50px'}">
            <h1>from initdata</h1>
            <div class="userguide">
                <div v-for="(r,index) in books1" :key='index'>
                <p>{{r.title}}</p>
                <p>{{r.author}}</p>
              </div>
            </div>
        </Content>
        <Content :style="{padding: '0 50px'}">
            <h1>from getmessage</h1>
            <div class="userguide">
                <div v-for="(r,index) in books2" :key='index'>
                <p>{{r.title}}</p>
                <p>{{r.author}}</p>
              </div>
            </div>
        </Content>
    </Layout>
</template>

<script>
export default {
    data () {
        return {
          books1: [],
          books2: [],
          news: [{
                    'title': 'news1',
                    'author': 'author2'
                }],
        }
    },
    methods: {
        initData() {
                this.$axios.get("/api", {}).then(res => {
                    this.books1 = res.data.books;
                });
        },
        getMessage() {
          const path = '/api';
          this.$axios //得加上this. 才行，ajax或者axios无所谓，加上this就行
            .get(path)
            .then(res => {
               this.books2 = res.data.books;
            })
            .catch(error => {
              console.log(error);
            });
        },
        sendMessage() {
            $axios
                .post("/api",data)
                .then((res) => {
                    console.log(res.data.news);
                })
                .catch(error => {
                    console.log(error);
                });
        }

    },
    created() {
      this.initData();
      this.getMessage();
      this.sendMessage();
    },
}
</script>
