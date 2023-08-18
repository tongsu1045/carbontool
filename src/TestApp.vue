<template>
    <div id="app">
        <img alt="Vue logo" src="./assets/logo.png" />
        <h1>{{books}}</h1>
    </div>
</template>
<script>
export default {
    name: "App",
    data() {
        return {
            books: "eeeeeee"
            };
        },
        methods: {
            initData() {
                this.$ajax.get("/", {}).then(res => {
                    this.books = res.data.books;
                });
            }
        },
        mounted() {
            this.initData();
        }
};
</script>
<style>
    #app {
        font-family: Avenir, Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-align: center;
        color: #2c3e50;
        margin-top: 60px;
    }
</style>
